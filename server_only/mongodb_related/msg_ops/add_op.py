# add_op.py

from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from bson import ObjectId

# Add msg to the msg history in a room
def add_msg_to_history(room_code, sender_id, sender_name, msg):
    # Generate a metadata for msg in the following format
    # Note: sender_id must be unique; sender_name can be duplicate.
    def gen_metadata(sender_id, sender_name, msg):
        return {
            'sender_id': sender_id,
            'sender_name': sender_name,
            'message': msg
        }
    
    # Convert room_code to room_id for generalization (using only room_id to execute DB operations)
    room_id = room_code_to_room_id(room_code)
    
    if room_id:
        msg_with_metadata = gen_metadata(sender_id, sender_name, msg)
        rooms_collection.update_one(
            {'_id': ObjectId(room_id)},
            {'$push': {'msg_list': msg_with_metadata}}
        )
        print(f'Successfully added msg to the msg_list of room with room_code [{room_code}].')
    else: 
        print(f'Error in add_msg(). Room with room_code [{room_code}] does not exist.')
    return    
