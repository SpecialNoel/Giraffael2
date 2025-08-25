# general_op.py

from v3src.server.database.mongodb_initiator import rooms_collection

# check if the given room code exists in the rooms_collection
def room_code_exists_in_collection(roomCode):
    room = rooms_collection.find_one(
        {'roomCode': roomCode}
    )   
    return True if room is not None else False
