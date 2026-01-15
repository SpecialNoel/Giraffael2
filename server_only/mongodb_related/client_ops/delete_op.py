# delete_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from msg_ops.general_op import roomCode_to_roomID
from mongodb_initiator import rooms_collection

from bson import ObjectId


def delete_client_to_list(address, roomCode):
    roomID = roomCode_to_roomID(roomCode)

    if roomID:
        rooms_collection.update_one(
            {'_id': ObjectId(roomID)},
            {'$pull': {'clientList': {'address': address}}}
        )
        print(f'Successfully deleted client with address [{address}] from the clientList of room with roomCode [{roomCode}].')
    else: 
        print(f'Error in delete_client_to_list(). Room with roomCode [{roomCode}] does not exist.')
    return
