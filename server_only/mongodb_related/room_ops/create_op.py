# create_op.py

from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from server_only.mongodb_related.mongodb_initiator import rooms_collection

def create_room(room_code, room_name='NewRoom'):
    if room_code_to_room_id(room_code) != None:
        print(f'Error in create_room(). Room with room_code [{room_code}] already exists.')
        return
    room_data = {
        'room_code': room_code,
        'room_name': room_name,
        'client_list': [],
        'msg_list': [],
        'file_list': []
    }
    room_inserted_id = rooms_collection.insert_one(room_data).inserted_id
    print(f'Created room in DB with room_code [{room_code}]. ' +
          f'room_id is [{room_inserted_id}].')
    return
