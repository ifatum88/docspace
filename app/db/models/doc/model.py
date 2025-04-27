from core.mongo import MongoModel

class Doc(MongoModel):

    _collection_name = "docs"
    _fields = [
        "type",
        "content",
        "author",
        "created",
        "updated",
        "updater"
    ]