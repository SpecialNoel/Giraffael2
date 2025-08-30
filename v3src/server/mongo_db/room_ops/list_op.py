# list_op.py

from v3src.server.mongo_db.mongodb_initiator import rooms_collection

def get_room_codes():
    roomCodes = []
    
    rooms = rooms_collection.find({}, {'roomCode': 1})
    for room in rooms:
        roomCodes.append(room['roomCode'])

    return roomCodes
