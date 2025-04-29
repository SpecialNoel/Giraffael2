# msg_operations.py

# Sorts of MongoDB operations such as listing, adding and deleting msg in each room.

from pymongo import MongoClient

# Connect to MongoDB with the connection string for Giraffael2DB
uri = ('mongodb+srv://jianminglin2893:cbVSqJdDMIUnso6Q' + 
       '@ac-os3juge.wu2ivo7.mongodb.net/Giraffael2DB' + 
       '?retryWrites=true&w=majority&tls=true')
mongoClient = MongoClient(uri, serverSelectionTimeoutMS=3000)

db = mongoClient['Giraffael2DB']
rooms_collection = db['Rooms'] # the "Rooms" collection


# Generate a metadata for msg in the following format
def generate_metadata_for_msg(senderID, senderName, msg):
    return {
        'senderID': senderID,
        'senderName': senderName,
        'message': msg
    }

# Add msg to the msg history in a room
def add_msg_to_msg_history(roomCode, senderID, senderName, msg):
    room = rooms_collection.find_one(
        {'roomCode': roomCode}
    )
    if room: 
        msgWithMetadata = generate_metadata_for_msg(senderID, senderName, msg)
        rooms_collection.update_one(
            {'roomCode': roomCode},
            {'$push': {'msgList': msgWithMetadata}}
        )
        print(f'Successfully added msg to the msgList.')
    else: 
        print(f'Error in add_msg_to_msg_history(). Room with roomCode [{roomCode}] does not exist.')
    return    

# List out all messages sent over this room
def list_msg_history(roomCode):
    room = rooms_collection.find_one(
        {'roomCode': roomCode}
    )
    if room:
        print(f'Msg history stored in room [{roomCode}]:')
        msgMetadatas = room['msgList']
        for msgMetadata in msgMetadatas:
            print(f'[{msgMetadata['senderName']}]: [{msgMetadata['message']}]')
        print()
    else:
        print(f'Error in list_msg_history(). Room with roomCode [{roomCode}] does not exist.')
    return

# Clear all message history happened in this room
def clear_msg_history(roomCode):
    room = rooms_collection.find_one(
        {'roomCode': roomCode}
    )
    if room:
        rooms_collection.update_one(
            {'roomCode': roomCode},
            {'$set': {'msgList':[]}}
        )
        print(f'Successfully cleared msg history in this room.')
    else: 
        print(f'Error in clear_msg_history(). Room with roomCode [{roomCode}] does not exist.')
    return
