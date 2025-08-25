# clear_op.py

from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.database.mongodb_initiator import rooms_collection

# Clear all message history happened in this room
def clear_msg_history(roomCode):
    if room_code_exists_in_collection(roomCode):
        rooms_collection.update_one(
            {'roomCode': roomCode},
            {'$set': {'msgList':[]}}
        )
        print(f'Successfully cleared msg history in room with room code [{roomCode}].')
    else: 
        print(f'Error in clear_msg(). Room [{roomCode}] does not exist.')
    return
