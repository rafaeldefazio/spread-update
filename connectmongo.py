from pymongo import MongoClient
import settings

cliente = MongoClient(settings.MONGO_URL, int(settings.MONGO_PORT))
banco = cliente[settings.MONGO_DB]