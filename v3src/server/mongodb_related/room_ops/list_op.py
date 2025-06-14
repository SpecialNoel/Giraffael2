# list_op.py

from v3src.server.mongodb_related.mongodb_initiator import rooms_collection

def get_roomCodes():
    roomCodes = []
    
    rooms = rooms_collection.find({}, {'roomCode': 1})
    for room in rooms:
        roomCodes.append(room['roomCode'])

    return roomCodes
