# clear_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from msg_ops.general_op import roomCode_to_roomID
from mongodb_initiator import rooms_collection

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
