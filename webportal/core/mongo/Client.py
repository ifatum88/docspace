from pymongo import MongoClient as mc
from config import Config

MongoClient = mc(Config.MONGO_URL)[Config.MONGO_DATABASE_NAME]
