# list_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from mongodb_initiator import rooms_collection

def get_roomCodes():
    roomCodes = []
    
    rooms = rooms_collection.find({}, {"roomCode": 1})
    for room in rooms:
        roomCodes.append(room['roomCode'])

    return roomCodes
