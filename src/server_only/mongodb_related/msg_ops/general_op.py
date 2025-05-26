# general_op.py

from src.server_only.mongodb_related.mongodb_initiator import rooms_collection

# get roomID with the roomCode of a room, if any
def roomCode_to_roomID(roomCode):
    room = rooms_collection.find_one(
        {'roomCode': roomCode}
    )   
    return room['_id'] if room is not None else None
