# delete_op.py

from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from bson import ObjectId

def delete_client_to_list(address, room_code):
    room_id = room_code_to_room_id(room_code)

    if room_id:
        rooms_collection.update_one(
            {'_id': ObjectId(room_id)},
            {'$pull': {'client_list': {'address': address}}}
        )
        print(f'Successfully deleted client with address [{address}] from the client_list of room with room_code [{room_code}].')
    else: 
        print(f'Error in delete_client_to_list(). Room with room_code [{room_code}] does not exist.')
    return
