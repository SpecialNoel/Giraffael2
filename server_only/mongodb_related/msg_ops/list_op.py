# list_op.py

from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from bson import ObjectId

# List out all messages sent over this room
def list_msg_history(room_code):
    room_id = room_code_to_room_id(room_code)

    if room_id:
        print(f'Msg history stored in room with room_code [{room_code}]:')
        room = rooms_collection.find_one(
            {'_id': ObjectId(room_id)}
        )
        msg_metadata_list = room['msg_list']
        for msg_metadata in msg_metadata_list:
            print(f'[{msg_metadata['sender_name']}]: [{msg_metadata['message']}]')
    else:
        print(f'Error in list_msg(). Room with room_code [{room_code}] does not exist.')
    return
