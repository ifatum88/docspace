from pymongo import MongoClient

def init_mongo(app):
    return MongoClient(app.config["MONGO_URL"])[app.config["MONGO_DATABASE_NAME"]]