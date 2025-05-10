# mongodb_initiator.py

import gridfs
from pymongo import MongoClient

# Connect to MongoDB with the connection string for Giraffael2DB
uri = ('mongodb+srv://jianminglin2893:cbVSqJdDMIUnso6Q' + 
       '@ac-os3juge.wu2ivo7.mongodb.net/Giraffael2DB' + 
       '?retryWrites=true&w=majority&tls=true')
mongoClient = MongoClient(uri, serverSelectionTimeoutMS=3000)
db = mongoClient['Giraffael2DB'] 
rooms_collection = db['Rooms'] # the 'Rooms' collection
gfs = gridfs.GridFS(db)
