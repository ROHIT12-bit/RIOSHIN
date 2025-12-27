from pymongo import MongoClient
from bot import config

client = MongoClient(config.MONGO_URI)
db = client.get_database()

approved_users = db.approved_users
banned_users = db.banned_users
blacklist = db.blacklist
settings = db.settings
logs = db.logs
stats = db.stats
