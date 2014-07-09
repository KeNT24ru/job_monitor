from pymongo import MongoClient

db = MongoClient()['job']
db.project.ensure_index('status')
