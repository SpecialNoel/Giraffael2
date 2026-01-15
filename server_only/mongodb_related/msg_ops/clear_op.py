# clear_op.py

from server_only.mongodb_related.msg_ops.general_op import roomCode_to_roomID
from server_only.mongodb_related.mongodb_initiator import rooms_collection
from bson import ObjectId

# Clear all message history happened in this room
def clear_msg_history(roomCode):
    roomID = roomCode_to_roomID(roomCode)
    
    if roomID:
        rooms_collection.update_one(
            {'_id': ObjectId(roomID)},
            {'$set': {'msgList':[]}}
        )
        print(f'Successfully cleared msg history in room with roomCode [{roomCode}].')
    else: 
        print(f'Error in clear_msg(). Room with roomCode [{roomCode}] does not exist.')
    return
