from pymongo import MongoClient
from pymongo.database import Database
from enum import Enum

import json
import jsonschema

class ModelFieldTypes(Enum):
    STRING = "string"
    INT = "int"

class ModelField:

    def __init__(self, field_type:ModelFieldTypes, name:str=None, val=None, rule:str=None):
        self.name = name
        self.type = field_type
        self.val = self.__set_val_by_type(val)
        self.rule = rule

    def __set_val_by_type(self, val):
        return val

    def __repr__(self):
        return f"<{self.__class__.__name__}. Name={self.name}, Type={self.type}, Val={self.val}>"

    def __str__(self):
        return f"<{self.__class__.__name__}. Name={self.name}, Type={self.type}, Val={self.val}>"

class ModelFabric(type):
    def __new__(cls, name, bases, dct):
        new_cls = super().__new__(cls, name, bases, dct)
        return new_cls
    
class ModelMeta():

    _schema = None

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
        self.schema = self.__get_schema()
        self.fields = self.__set_fields_list()

    def __set_fields_list(self):

        # получение полей из схемы монго
        # обработка исключенией - если поля с одинаковыми именами
        # обработка исключенией - если в номго нет схемы и _get_schema_from_mongo == True
        # добавить получение из много только если _get_schema_from_mongo == True

        model_fields = [field for field in self._model_fields]

        # Выход, если не надо брать схему их монго
        if not self._get_schema_from_mongo:
            return model_fields
        
        # Выход, если схема из монго пустая

        mongo_fields = [ModelField("test", "String")]

        return model_fields + mongo_fields

    def __get_schema(self) -> dict:

        coll_info = self._db.command("listCollections", filter={"name": self.collection})
        schema = coll_info["cursor"]["firstBatch"][0].get("options", {}).get("validator", {})
    
        # тут надо убедиться, что  словарь высегда выводит, если нет схемы валидации

        return schema

    def __repr__(self):
        return f"<{self.__class__.__name__}. Collection={self.collection}, Fields = {self.fields}>"

    def __str__(self):
        return f"<{self.__class__.__name__}. Collection={self.collection}, Fields = {self.fields}>"

class QuerySet():
    def __init__(self):
        pass

class ModelBase(metaclass=ModelFabric):

    # Базовые атрибуты при инициализации экземпляра класса
    _collection = None
    _db = None

    # Внутренние атрибуты, которые при желании можно переопределить внутри модели
    _get_schema_from_mongo = True

    def __init__(self, db:Database):
        self._db = db
        self._model_fields = self.__set_model_fields()

        self.meta = ModelMeta(
            self._db,
            self._collection,
            self._get_schema_from_mongo,
            self._model_fields)

    def __set_model_fields(self) -> list:
        fields = []

        for key in dir(self):
            if not key.startswith('_') and not callable(getattr(self, key)):

                # Вот тут надо сделать проверку, что поле пришло ModelField
                # Если нет, то ничего не делать и писать ошибку в лог
                # Подключить блять уже наконец логирование ...
                
                field_type_meta = getattr(self, key)

                fields.append(ModelField(
                    name=key,
                    field_type=field_type_meta.type,
                    val=field_type_meta.val)
                    )

        return fields
                                                        
    def to_dict(self):
        pass

    def to_json(self):
        pass

    def all(self):
        pass

    def get_one(self):
        pass

class Page(ModelBase):

    # Указал имя коллекции
    _collection = "pages"

    # Определил 2 поля внутри модели
    new_field_one = ModelField(field_type=ModelFieldTypes.STRING, val="test")
    new_field_two = ModelField(field_type=ModelFieldTypes.STRING)

# #########

db = MongoClient("mongodb://localhost:27017")["docspace"]

_obj = Page(db=db)

print ("")
print (type(_obj))
print (_obj.meta.__repr__)
# print (dir(_obj))


# _obj = type("ClassName1", (MetaClass,), {})("val1", "val2")
