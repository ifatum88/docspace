from json import dumps

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