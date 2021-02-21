import pymongo

client = pymongo.MongoClient(
    "mongodb://developer:masterbaiter@192.168.0.100:27017/masterquoter"
)  # defaults to port 27017

db = client.masterquoter

# print the number of documents in a collection
print(db.masterquoter.estimated_document_count())
