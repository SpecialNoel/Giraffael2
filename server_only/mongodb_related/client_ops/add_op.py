# add_op.py

from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from bson import ObjectId

def add_client_to_list(client_obj, room_code):
    room_id = room_code_to_room_id(room_code)

    if room_id:
        rooms_collection.update_one(
            {'_id': ObjectId(room_id)},
            {'$push': {'client_list': client_obj.to_dict()}}
        )
        print(f'Successfully added client [{client_obj.get_address()}] to the client_list of room with room_code [{room_code}].')
    else: 
        print(f'Error in add_client_to_list(). Room with room_code [{room_code}] does not exist.')
    return 
