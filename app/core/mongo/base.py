class MongoAccessor:
    def __init__(self, model, db):
        self._model = model # Получение модели
        self._collection = db[model._collection_name] # Получение коллекции для обработки в модели

    def all(self):
        """
        Метод выводит всю коллекцию
        """

        return [self._model(doc) for doc in self._collection.find()]
    
    def get_one(self, query: dict) -> dict:
        result = self._collection.find_one(query)
        return (self._model(result) if result else None)

class MongoModel:
    _collection_name = None # Объявляется внутри модели
    _fields = None # Объявляется внутри модели

    def __init__(self, data:dict):
        # Данные из MongoDB для оработки моделью
        self._data = data

        # Сразу добавляем ID, чтобы каждый раз не описывать его в модели
        self.id = data.get("_id")
        
        # Добавлеяем атрибуты из модели и заполняем их значениями из Mongo
        for field in self._fields:
            val = data.get(field)

            # if val:
            setattr(self, field, val)

    def to_dict(self):
        """
        Функция переводит объект Model в dict
        """
        # Складываем в словарь все атрибуты модели
        ret = {field: getattr(self, field) for field in self._fields}
        # Явно добавляем ID документа
        ret["id"] = str(self.id)
        return ret

    @classmethod
    def use(cls, db):
        # Класс метод для инициализации модели
        return MongoAccessor(cls, db)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.to_dict()}>"