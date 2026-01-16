# clear_op.py

from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from bson import ObjectId

# Clear all message history happened in this room
def clear_msg_history(room_code):
    room_id = room_code_to_room_id(room_code)
    
    if room_id:
        rooms_collection.update_one(
            {'_id': ObjectId(room_id)},
            {'$set': {'msg_list':[]}}
        )
        print(f'Successfully cleared msg history in room with room_code [{room_code}].')
    else: 
        print(f'Error in clear_msg(). Room with room_code [{room_code}] does not exist.')
    return
