from pymongo import MongoClient
from pymongo.database import Database
from enum import Enum
from services import get_logger
from bson import ObjectId
from typing import Union, List, Optional
from dataclasses import dataclass, field

import json
import jsonschema

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
    val: Optional[any] = None
    is_required: bool = False
    validation_rules: dict = field(default_factory=dict)

    def __repr__(self):
        return f"<{self.__class__.__name__}. Name={self.name}, Type={self.type}, Val={self.val}>"

    def __str__(self):
        return f"<{self.__class__.__name__}. Name={self.name}, Type={self.type}, Val={self.val}>"
    
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

    def __set_fields_list(self):
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

    def len(self):
        return len(self._data)

    def to_list(self):
        return list(self._data)

    def __repr__(self):
        return f"<QuerySet Model={self.model_name}, Size={self.len()}>"

class ModelBase(metaclass=ModelFabric):

    # Базовые атрибуты при инициализации экземпляра класса
    _collection = None
    _model = None

    # Внутренние атрибуты, которые при желании можно переопределить внутри модели
    _get_schema_from_mongo = True

    def __init__(self, db:Database):
        self._db = db
        self.meta = ModelMeta(
            db=self._db,
            collection=self._collection,
            get_schema_from_mongo=self._get_schema_from_mongo,
            model_fields=self.__get_model_fields()
            )

    def __get_model_fields(self) -> list:
        fields = []

        # Перебираем все атрибуты класса
        for key in dir(self):

            # Убираем методы и служебние атрибуты, которые начинаются с _
            if not key.startswith('_') and not callable(getattr(self, key)):
                
                field_candidate = getattr(self, key)

                # Не обрабатываем атрибуты, которые не ModelField
                if not isinstance(field_candidate, ModelField):
                    self._logger.warning(f"Атрибут '{key}' не является экземпляром ModelField")
                    continue
                
                # Добавляем атрибут в модель
                fields.append(ModelField(
                    name=key,
                    type=field_candidate.type,
                    val=field_candidate.val,
                    source=ModelFieldSources.MODEL)
                    )

        return fields
    
    def __transform_mongo_data_to_model(self):
        pass

    def __validate_mongo_data(self):
        pass
    
    def all(self):
        pass

    def get_one(self):
        pass

    def get_many(self):
        pass
                                                        
    def to_dict(self):
        pass

    def to_json(self):
        pass


        pass

class Pages(ModelBase):

    _collection = "pages"
    _model = "Page"

    # Определил 3 поля внутри модели длч тестирования
    new_field_one = ModelField(type=ModelFieldTypes.STRING, val="test") # Тут заполнение константой
    new_field_three = ModelField(type=ModelFieldTypes.STRING)
    new_field_four = ModelField(type=ModelFieldTypes.INT) # А тут будет динамическа заполняться

# #########

db = MongoClient("mongodb://localhost:27017")["docspace"]

_obj = Pages(db=db)

print ("")
print (type(_obj))
print ()
# print (dir(_obj))
# _obj = type("ClassName1", (MetaClass,), {})("val1", "val2")

# for field in _obj.meta.fields:
#     print (f"Name = {field.name}, type={field.type}, source={field.source}, val={field.val}, is_required={field.is_required}, rules={field.validation_rules}")


_tst = QuerySet("Test", [n for n in range(5)])
print(_tst)

for item in _tst:
    print (item)

_tst.append(5)
print(_tst)

print(_tst.to_list())