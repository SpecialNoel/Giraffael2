# add_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from msg_ops.general_op import roomCode_to_roomID
from mongodb_initiator import rooms_collection

from bson import ObjectId

 
# Add msg to the msg history in a room
def add_msg_to_history(roomCode, senderID, senderName, msg):
    # Generate a metadata for msg in the following format
    # Note: senderID must be unique; senderName can be duplicate.
    def gen_metadata(senderID, senderName, msg):
        return {
            'senderID': senderID,
            'senderName': senderName,
            'message': msg
        }
    
    # Convert roomCode to roomID for generalization (using only roomID to execute DB operations)
    roomID = roomCode_to_roomID(roomCode)
    
    if roomID:
        msgWithMetadata = gen_metadata(senderID, senderName, msg)
        rooms_collection.update_one(
            {'_id': ObjectId(roomID)},
            {'$push': {'msgList': msgWithMetadata}}
        )
        print(f'Successfully added msg to the msgList of room with roomCode [{roomCode}].')
    else: 
        print(f'Error in add_msg(). Room with roomCode [{roomCode}] does not exist.')
    return    
