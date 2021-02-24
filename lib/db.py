import pymongo
from os import getenv
from dotenv import load_dotenv

load_dotenv()

print(getenv("DATABASE_URL"))
client = pymongo.MongoClient(getenv("DATABASE_URL"))
db = client.masterquoter