# room_operations.py

# Sorts of MongoDB operations such as listing, adding and deleting msg in each room.

from pymongo import MongoClient
import gridfs

# Connect to MongoDB with the connection string for Giraffael2DB
uri = ('mongodb+srv://jianminglin2893:cbVSqJdDMIUnso6Q' + 
       '@ac-os3juge.wu2ivo7.mongodb.net/Giraffael2DB' + 
       '?retryWrites=true&w=majority&tls=true')
mongoClient = MongoClient(uri, serverSelectionTimeoutMS=3000)

db = mongoClient['Giraffael2DB']
rooms_collection = db['Rooms'] # the "Rooms" collection
gfs = gridfs.GridFS(db)


# Create a room in the DB
def create_room(roomCode, roomName='NewRoom'):
    room_data = {
        'roomCode': roomCode,
        'roomName': roomName,
        'clientList': [],
        'msgList': [],
        'fileList': []
    }
    roomInsertedID = rooms_collection.insert_one(room_data).inserted_id
    print(f'Created room in DB with roomCode [{roomCode}]. ' +
          f'Room Insert ID is [{roomInsertedID}].')
    return
    
# Delete a room in the DB (based on roomCode)
def delete_room(roomCode):
    rooms_collection.delete_one({"roomCode": roomCode})
    print(f'Deleted room with roomCode [{roomCode}].')
    return

if __name__=='__main__':  
    roomCode = 'f9wa8rq9fqvg0qj'
    create_room(roomCode)
    