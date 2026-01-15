# delete_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from file_ops.delete_op import delete_all_files
from mongodb_initiator import rooms_collection
from msg_ops.general_op import roomCode_to_roomID

from bson import ObjectId
from bson.errors import InvalidId


# Delete a room in the DB (based on ObjectID of the room)
def delete_room(roomCode):
    roomID = roomCode_to_roomID(roomCode)
    try:
        room = rooms_collection.find_one(
            {'_id': ObjectId(roomID)}
        )
    except InvalidId:
        print(f'Error in upload_file(). roomID [{roomID}] is invalid.')
        return -1
    
    # Delete all files existed in that room first
    delete_all_files(roomID)
    # Delete the room in database
    rooms_collection.delete_one({'_id': ObjectId(roomID)})
    print(f'Successfully deleted room with roomID [{roomID}].')
    return
