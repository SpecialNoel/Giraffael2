# general_op.py

from v3src.server.mongo_db.mongodb_initiator import rooms_collection

# check if the given room code exists in the rooms_collection
def room_code_exists_in_collection(room_code):
    room = rooms_collection.find_one(
        {'roomCode': room_code}
    )   
    return True if room is not None else False
