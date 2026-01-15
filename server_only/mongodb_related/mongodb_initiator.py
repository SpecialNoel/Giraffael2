# mongodb_initiator.py

import gridfs
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()
database_password = os.getenv('DATABASE_PASSWORD')

# Connect to MongoDB with the connection string for GiraffaelDB
uri = (f'mongodb+srv://jianminglin2893:{database_password}' + 
       '@cluster0.wu2ivo7.mongodb.net/GiraffaelDB' + 
       '?retryWrites=true&w=majority&tls=true')
mongoClient = MongoClient(uri, serverSelectionTimeoutMS=3000)
db = mongoClient['GiraffaelDB']
users_collection = db['Users']
rooms_collection = db['Rooms']
gfs = gridfs.GridFS(db)
