import pymongo

client = pymongo.MongoClient(
    "mongodb://developer:masterbaiter@192.168.0.100:27017/masterquoter"
)

db = client.masterquoter

for i in range(10000):
    db.users.insert_one({"user": "random person"})