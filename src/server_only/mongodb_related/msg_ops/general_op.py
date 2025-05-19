# general_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from mongodb_initiator import rooms_collection

# get roomID with the roomCode of a room, if any
def roomCode_to_roomID(roomCode):
    room = rooms_collection.find_one(
        {'roomCode': roomCode}
    )   
    return room['_id'] if room is not None else None
