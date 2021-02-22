import pymongo

client = pymongo.MongoClient(
    "mongodb://developer:masterbaiter@192.168.0.100:27017/masterquoter"
)

db = client.masterquoter

users = db.users.find({})
servers = db.servers.find({})
db.servers.find

# print the number of documents in a collection
for user in users:
    print(f"USER: {user}")

for server in servers:
    print(f"SERVER: {server}")
