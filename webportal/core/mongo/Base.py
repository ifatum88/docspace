from pymongo.database import Database
from pymongo.cursor import Cursor

from .Const import BSON_TO_JSON_TYPE, JSON_VALIDATION_RULES
from .Fields import ModelFieldTypes, ModelField, ModelFieldSources
from .Transformer import ModelFieldValueTransformer
from .QuerySet import QuerySet
from core.utils import get_logger

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
    
class ModelMetaClass(metaclass=ModelFabric):

    def __init__(self, doc:dict, fields:list):
        self.__set_attributes(doc, fields)

    def __set_attributes(self, doc: dict, fields: list):
        # TBD Добавить получение динамических значений из вызов функций внутри модели (пока такое не надо)

        for field in fields:
            key = field.name
            val = doc.get(key, field.default_val) # Пытаемся получить значение из БД, если его нет, ставим default_val из ModelField
            val = self.__transform_field_value_type(key, val, field.type, field.validation_rules)
            setattr(self, field.name, val)

    def __transform_field_value_type(self, name, val, field_type, validation_rules):
        """
        Приводит значение к одному из допустимых типов внутри jsonschema
        """

        return ModelFieldValueTransformer.transform(
            model=self.__class__.__name__,
            field_name=name,
            val=val, 
            field_type=field_type,
            validation_rules=validation_rules, 
            logger=self._logger)

    # Доделаю валидацию в будущем, если она будет нужна
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
            if not key.startswith('_') and not callable(value):
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
        data = self._db[self._collection].find_one(query)

        if data:
            return self.__transform_mongo_data_to_model([data]).first()

    def find_many(self, query:dict):
        data = self._db[self._collection].find(query)
        return self.__transform_mongo_data_to_model(data)