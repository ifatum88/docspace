from pymongo import MongoClient
from pymongo.database import Database
from pymongo.cursor import Cursor
from enum import Enum
from services import get_logger
from bson import ObjectId
from typing import Union, List, Optional
from dataclasses import dataclass, field
from jsonschema import validate, ValidationError
from datetime import datetime
from json import dumps

# Соответствие bsonType -> type
BSON_TO_JSON_TYPE = {
    "objectId": "objectId",
    "string": "string",
    "int": "integer",
    "long": "integer",
    "double": "number",
    "bool": "boolean",
    "date": "string", 
    "array": "array",
    "object": "object"
}

JSON_VALIDATION_RULES = ["pattern", "minLength", "maxLength", "minItems", "format", "minimum"]

class ModelFieldTypes(Enum):
    STRING = "string"
    INT = "integer"
    OBJECTID = "objectId"
    BOOLEAN = "boolean"
    NUMBER = "number"
    ARRAY = "array"
    DATE = "date"

    def __str__(self):
        return self.value

@dataclass(frozen=True)
class ModelFieldSources(Enum):
    MODEL = "model"
    MONGO = "mongo"

@dataclass(frozen=True)
class ModelField:
    type: Union['ModelFieldTypes', List['ModelFieldTypes']]
    source: ModelFieldSources = ModelFieldSources.MODEL
    name: Optional[str] = None
    default_val: Optional[any] = None
    is_required: bool = False
    validation_rules: dict = field(default_factory=dict)

    def __repr__(self):
        return f"<{self.__class__.__name__}. Name={self.name}, Type={self.type}, Val={self.default_val}>"

    def __str__(self):
        return f"<{self.__class__.__name__}. Name={self.name}, Type={self.type}, Val={self.default_val}>"
    
    def __eq__(self, other):
        return isinstance(other, ModelField) and self.name == other.name and self.type == other.type

    def __hash__(self):
        return hash((self.name, str(self.type)))

    def __post_init__(self):
        if not isinstance(self.type, (ModelFieldTypes, list)):
            raise TypeError(f"Invalid type: {self.type}")
        
class ModelFabric(type):
    def __new__(cls, name, bases, dct):
        new_cls = super().__new__(cls, name, bases, dct)

        if not hasattr(new_cls, '_logger'):
            new_cls._logger = get_logger(name=f"{new_cls.__module__}.{name}")
        
        return new_cls

class ModelMeta(metaclass=ModelFabric):

    _schema = None
    _mongo_json_map = {
        "fields": [],
        "types": []
    }

    def __init__(
            self, 
            db:Database, 
            collection:str, 
            get_schema_from_mongo:bool,
            model_fields:list):
        
        self._db = db # Клиент Mongo
        self._get_schema_from_mongo = get_schema_from_mongo # Нужно ли брать данные коллекции из монго?
        self._model_fields = model_fields # Поля, которые определены внутри модели

        self.collection = collection
        self.jsonschema = self.__get_schema()
        self.fields = self.__set_fields_list()

    def __set_fields_list(self) -> list:
        """Собираем все поля в мету модели"""
        model_fields = self.__collect_model_fields()
        mongo_fields = self.__collect_mongo_fields()

        return self.__merge_fields(model_fields, mongo_fields)
    
    def __collect_model_fields(self) -> list:
        """Собираем поля, определенные вручную внутри модели"""
        return [field for field in self._model_fields]
    
    def __collect_mongo_fields(self) -> list:
        """Собираем поля из схемы MongoDB"""
        mongo_fields = []

        # Выход, если не надо брать схему их монго
        if not self._get_schema_from_mongo:
            return []

        # Выход, если нет jsonschema
        if not isinstance(self.jsonschema, dict):
            self._logger.warning(f"Нет $jsonSchema для обработки внутри модели")
            return []

        # Добавление полей из jsonschema в метаданные модели
        for field_name, field_meta in self.jsonschema.get('properties', {}).items():
            validation_rules = {
                rule: field_meta[rule]
                for rule in JSON_VALIDATION_RULES
                if rule in field_meta
            }

            field_type = None
            if 'type' in field_meta:
                field_type = ModelFieldTypes(field_meta['type'])
            elif 'anyOf' in field_meta:
                field_type = [
                    ModelFieldTypes(option.get('type'))
                    for option in field_meta['anyOf']
                    if 'type' in option
                ]

            mongo_fields.append(ModelField(
                type=field_type,
                source=ModelFieldSources.MONGO,
                name=field_name,
                is_required=True if field_name in self.jsonschema.get('required', []) else False,
                validation_rules=validation_rules
            ))

        return mongo_fields        
    
    def __merge_fields(self, model_fields: list, mongo_fields: list) -> list:
        """Объединяем поля модели и Mongo, устраняя дубликаты"""
        fields_by_name = {field.name: field for field in model_fields}

        for mongo_field in mongo_fields:
            if mongo_field.name in fields_by_name:
                self._logger.warning(
                    f"Дублирующееся поле '{mongo_field.name}' обнаружено: "
                    f"предпочтение отдано схеме MongoDB, поле из модели проигнорировано."
                )
            fields_by_name[mongo_field.name] = mongo_field

        return list(fields_by_name.values())

    def __get_schema(self) -> dict:
        """Получает и преобразует схему MongoDB"""
        coll_info = self._db.command("listCollections", filter={"name": self.collection})
        mongo_schema = coll_info["cursor"]["firstBatch"][0].get("options", {}).get("validator", {})
        mongo_schema = mongo_schema.get("$jsonSchema")

        if not mongo_schema:
            self._logger.warning(f"Некорректная mongo-scheme, нет '$jsonSchema'")
            return {}

        if not (
            mongo_schema.get('bsonType')
            or mongo_schema.get('required')
            or mongo_schema.get('properties')
        ):
            self._logger.warning(f"Некорректная mongo-scheme, нет обязательных атрибутов 'bsonType' или 'required' или 'properties'")
            return {}

        return self.__transform_mongo_schema(mongo_schema)

    def __transform_mongo_schema(self, mongo_schema: dict) -> dict:
        """Преобразует MongoDB `$jsonSchema` в стандартную JSON Schema."""
        mongo_properties = mongo_schema.get("properties", {})
        required_fields = mongo_schema.get("required", [])
        json_properties = {}

        for field_name, field_info in mongo_properties.items():
            bson_type = field_info.get("bsonType")

            if isinstance(bson_type, list):
                any_of = [{"type": BSON_TO_JSON_TYPE.get(t, "string")} for t in bson_type]
                json_properties[field_name] = {"anyOf": any_of}
            else:
                json_type = BSON_TO_JSON_TYPE.get(bson_type, "string")
                prop = {"type": json_type}

                if bson_type == "date":
                    prop["format"] = "date-time"

                if bson_type == "array" and "items" in field_info:
                    item_bson_type = field_info["items"].get("bsonType")
                    prop["items"] = {
                        "type": BSON_TO_JSON_TYPE.get(item_bson_type, "string")
                    }

                json_properties[field_name] = prop

        return {
            "type": "object",
            "required": required_fields,
            "properties": json_properties
        }

    def __repr__(self):
        return f"<{self.__class__.__name__}. Collection={self.collection}, Fields = {self.fields}>"

    def __str__(self):
        return f"<{self.__class__.__name__}. Collection={self.collection}, Fields = {self.fields}>"
    
class ModelFieldValueTransformer:

    @staticmethod
    def __handle_special_types(val, t):
        """
        Обрабатывает специфические типы данных, которые требуют приведения или десериализации
        вручную, перед валидацией по jsonschema.

        Используется как предварительная стадия трансформации до основного кастинга типов.

        Args:
            val: Значение поля, которое нужно обработать.
            t (ModelFieldTypes): Целевой тип из перечисления ModelFieldTypes.

        Returns:
            Приведенное значение, если удалось выполнить конвертацию.
            None — если тип не требует спец. обработки или приведение не выполнено.

        Обрабатываемые типы:
        - OBJECTID: Преобразует строку или уже готовый ObjectId в ObjectId
        - DATE: Преобразует ISO-строку в datetime.datetime (aware)
        """

        # Обработка ObjectId: либо возвращаем как есть, либо преобразуем из строки
        if t == ModelFieldTypes.OBJECTID:
            return val if isinstance(val, ObjectId) else ObjectId(val)
        
        # Обработка даты: если уже datetime, вернуть как есть, иначе распарсить ISO 8601 строку
        if t == ModelFieldTypes.DATE:
            return val if isinstance(val, datetime) else datetime.fromisoformat(val.replace("Z", "+00:00"))
        
        # Для остальных типов ничего не делаем
        return None

    @staticmethod
    def transform(val, field_type, validation_rules=None, logger=None):
        """
        Преобразует и валидирует значение поля на основе допустимых типов и правил валидации.

        Эта функция обрабатывает случаи, когда поле может иметь один или несколько допустимых типов 
        (например, через `anyOf` в jsonschema), и пытается привести значение к первому подходящему типу.

        Аргументы:
            val: Значение, которое нужно привести.
            field_type: Один или список типов из ModelFieldTypes.
            validation_rules (dict): Правила валидации JSON Schema (pattern, minLength и т.д.)
            logger (logging.Logger): Логгер для фиксации ошибок, если передан.

        Возвращает:
            Приведённое значение, если один из типов прошёл валидацию и преобразование,
            иначе — оригинальное значение.
        """
        if val is None:
            return None

         # Приведение к списку (если один тип — оборачиваем в список)
        types = field_type if isinstance(field_type, list) else [field_type]

         # Пробуем по очереди все возможные типы
        for t in types:
            try:
                # Если требуется специальная обработка (DATE, OBJECTID)
                val = ModelFieldValueTransformer.__handle_special_types(val, t) or val
                
                # Формируем схему и добавляем валидаторы
                schema = {"type": t.value}
                if validation_rules:
                    schema.update(validation_rules)

                # Валидация по jsonschema
                validate(instance=val, schema=schema)

                # Если прошло валидацию — возвращаем приведённое значение
                return ModelFieldValueTransformer.__cast(val, t)

            except Exception as e:
                if logger:
                    logger.warning(f"[Transform] Не удалось преобразовать '{val}' в {t}: {e}")

         # Если не удалось привести ни к одному типу — логируем и возвращаем оригинал
        if logger:
            logger.warning(f"[Transform] Оставлено оригинальное значение '{val}' (не найдено подходящего типа)")

        return val

    @staticmethod
    def __cast(val, t: ModelFieldTypes):
        if t == ModelFieldTypes.STRING:
            return str(val)
        if t == ModelFieldTypes.INT:
            return int(val)
        if t == ModelFieldTypes.NUMBER:
            return float(val)
        if t == ModelFieldTypes.BOOLEAN:
            return bool(val)
        if t == ModelFieldTypes.ARRAY:
            return list(val)
        if t == ModelFieldTypes.OBJECT:
            return dict(val)
        return val  

class ModelMetaClass(metaclass=ModelFabric):

    def __init__(self, doc:dict, fields:list):
        self.__set_attributes(doc, fields)

    def __set_attributes(self, doc: dict, fields: list):
        # TBD Добавить получение динамических значений из вызов функций внутри модели (пока такое не надо)

        for field in fields:
            key = field.name
            val = doc.get(key) or field.default_val # Пытаемся получить значение из БД, если его нет, ставим default_val из ModelField
            val = self.__transform_field_value_type(val, field.type, field.validation_rules)
            setattr(self, field.name, val)

    def __transform_field_value_type(self, val, field_type, validation_rules):
        """
        Приводит значение к одному из допустимых типов внутри jsonschema
        """

        return ModelFieldValueTransformer.transform(val, field_type, validation_rules, logger=self._logger)

    # Напишу валидацию по правилам из схемы, если надо будет
    def __validate_field_value(self):
        pass

    def __attrs_list(self):
        return ", ".join(f"{k}: {v!r}" for k, v in self.__dict__.items())

    def __repr__(self):
        return f"Object=<{self.__class__.__name__}. Attrs=[{self.__attrs_list()}]>"

    def __str__(self):
        return f"Object=<{self.__class__.__name__}. Attrs=[{self.__attrs_list()}]>"
    
    def to_dict(self):
        return self.__dict__.copy()

class QuerySet:
    def __init__(self, model_name=None, data=None):
        self._data = data or []
        self.model_name = model_name

    def __iter__(self):
        return iter(self._data)

    def __getitem__(self, key):
        return self._data[key]

    def append(self, obj):
        self._data.append(obj)

    def __len__(self):
        return len(self._data)

    def to_list(self):
        return list(self._data)
    
    def first(self):
        return self._data[0] if self._data else None
    
    def to_dict_list(self):
        return [obj.to_dict() for obj in self._data]
    
    def to_json(self, **kwargs):
        return dumps(self.to_dict_list(), default=str, ensure_ascii=False, **kwargs)

    def __repr__(self):
        return f"<QuerySet Model={self.model_name}, Size={self.__len__()}>"
    
class ModelBase(metaclass=ModelFabric):

    # Базовые атрибуты при инициализации экземпляра класса
    _collection = None
    _model = None

    # Внутренние атрибуты, которые при желании можно переопределить внутри модели
    _get_schema_from_mongo = True

    def __init__(self, db:Database):
        self._db = db
        self._cache = None
        self.meta = ModelMeta(
            db=self._db,
            collection=self._collection,
            get_schema_from_mongo=self._get_schema_from_mongo,
            model_fields=self.__get_model_fields()
            )

    def __get_model_fields(self) -> list:
        fields = []

        for key, value in self.__class__.__dict__.items():
            if isinstance(value, ModelField):
                fields.append(ModelField(
                    name=key,
                    type=value.type,
                    default_val=value.default_val,
                    source=ModelFieldSources.MODEL
                ))
            else:
                self._logger.warning(f"Атрибут '{key}' не является экземпляром ModelField")

        return fields

    def __transform_mongo_data_to_model(self, data:Cursor) -> QuerySet:

        documents = list(data)
        MetaModelObject = type(self._model, (ModelMetaClass, ), {})
        ret = QuerySet([])

        # Возвращаем пустой QuerySet если запрос не вернул данных
        if not documents:
            return ret
        
        # Преобразуем словари в динамический объект, описанный внутри класса ModelMetaClass
        # Имя класса берется из self._model
        for doc in documents:
            ret.append(MetaModelObject(doc=doc, fields=self.meta.fields))
        
        return ret
    
    def get_all(self) -> QuerySet:

        data = self._db[self._collection].find()

        if self._cache:
            return self._cache
        self._cache = self.__transform_mongo_data_to_model(data)
        return self._cache

    def find_one(self, query:dict) -> QuerySet:
        data = [self._db[self._collection].find_one(query)]
        return self.__transform_mongo_data_to_model(data)

    def find_many(self, query:dict):
        data = self._db[self._collection].find(query)
        return self.__transform_mongo_data_to_model(data)

class Pages(ModelBase):

    _collection = "pages"
    _model = "Page"

    # Определил 3 поля внутри модели длч тестирования
    new_field_one = ModelField(type=ModelFieldTypes.STRING, default_val="test") # Тут заполнение константой
    new_field_three = ModelField(type=ModelFieldTypes.STRING)
    new_field_four = ModelField(type=ModelFieldTypes.INT) # А тут будет динамическа заполняться

# #########

db = MongoClient("mongodb://localhost:27017")["docspace"]

_obj = Pages(db=db)

print ("")
print (type(_obj), end="\n\n")
# print (type(_obj.all()))
_f = _obj.find_many({'order': 1})
print (type(_f))

for doc in _f:
    print (doc, end="\n\n")

print (f"Type = {type(_f.to_dict_list())}", _f.to_dict_list(), end="\n\n")
print (f"Type = {type(_f.to_json())}", _f.to_json(), end="\n\n")