import pymongo
from os import getenv
from dotenv import load_dotenv

load_dotenv()

client = pymongo.MongoClient(getenv("DATABASE_URL"))
db = client.masterquoter