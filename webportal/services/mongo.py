from pymongo import MongoClient
from flask import Flask

class Mongo:
    def __init__(self, app:Flask):
        self.url = app.config.extention.mongo['url']
        self.db = app.config.extention.mongo['database']

    def client(self):
        return MongoClient(self.url)[self.db]
