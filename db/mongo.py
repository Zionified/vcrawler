# -*- coding: utf-8 -*-

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


__MONGO_CLIENT__ = MongoClient(
    "mongodb+pymongo://localhost:27017", server_api=ServerApi("1")
)


def get_mongo_client():
    return __MONGO_CLIENT__
