# delete_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from mongodb_initiator import rooms_collection, gfs
from file_ops.general_op import roomCode_to_roomID

from bson import ObjectId
from bson.errors import InvalidId


# Delete a file in a room
def delete_file(fileID, roomCode):
    try:
        file = gfs.find_one({'_id': ObjectId(fileID)})
        if not file:
            print(f'Error in delete_file(). File with fileID [{fileID}] does not exist in database.')
            return
    except InvalidId:
        print(f'Error in delete_file(). fileID [{fileID}] is invalid.')
        
    roomID = roomCode_to_roomID(roomCode)
        
    # Test if given roomID is in invalid format
    try:
        room = rooms_collection.find_one(
            {'_id': ObjectId(roomID)}
        )
    except InvalidId:
        print(f'Error in delete_file(). roomID [{roomID}] is invalid.')
        return
    
    if file.metadata['roomID'] != roomID:
        print(f'Error in delete_file(). File with fileID [{fileID}] does not exist in room [{roomID}].')
        return 
    
    # Delete the file, indicated by the fileID, from the database
    gfs.delete(ObjectId(fileID))
    # Remove the filename, indicated by the fileID, from 'fileList' of this room    
    rooms_collection.update_one(
        {'_id': ObjectId(roomID)},
        {'$pull': {'fileList': {'fileID': ObjectId(fileID)}}}
    )
    print(f'Successfully deleted file with fileID [{fileID}] in room [{roomID}].')
    return

# Delete all files in a room
def delete_all_files(roomID):
    # Use roomID to get all fileIDs of the room, then use the fileIDs to delete all files
    try:
        files = gfs.find({'metadata.roomID': roomID})
    except InvalidId:
        print(f'Error in delete_all_files(). roomID [{roomID}] is invalid')
        return
    
    if not files.alive:
        print(f'There are no existing files in room [{roomID}].')
        return
    for file in files:
        print(f'FileID to be deleted: [{file._id}]')
        delete_file(file._id, roomID)
    print(f'Successfully deleted all files from room [{roomID}].')
    return
