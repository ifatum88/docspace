from core.mongo import MongoModel

class Page(MongoModel):

    _collection_name = "pages"
    _fields = [
        "name",
        "order",
        "child",
        "slug",
        "doc"
    ]