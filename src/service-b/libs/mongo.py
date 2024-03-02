from pymongo import MongoClient

client = MongoClient('mongodb://auuntoo:auuntoo@localhost:27017/')
db = client['otel_db']

def get_mongo_collection(collection_name: str):
    return db[collection_name]