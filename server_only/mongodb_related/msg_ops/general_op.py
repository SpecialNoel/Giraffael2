# general_op.py

from server_only.mongodb_related.mongodb_initiator import rooms_collection

# get room_id with the room_code of a room, if any
def room_code_to_room_id(room_code):
    room = rooms_collection.find_one(
        {'room_code': room_code}
    )   
    return room['_id'] if room is not None else None
