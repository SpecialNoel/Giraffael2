# list_op.py

from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from bson import ObjectId

def list_clients(room_code):
    room_id = room_code_to_room_id(room_code)

    if room_id:
        print(f'Clients in room with room_code [{room_code}]:')
        room = rooms_collection.find_one(
            {'_id': ObjectId(room_id)}
        )
        client_list = room['client_list']
        for client in client_list:
            print(f'--uuid:[{client['uuid']}]. address:[{client['address']}]. username:[{client['username']}]')
    else: 
        print(f'Error in add_client_to_list(). Room with room_code [{room_code}] does not exist.')
    return 
