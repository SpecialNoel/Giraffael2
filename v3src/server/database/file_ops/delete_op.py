# delete_op.py

from bson import ObjectId
from bson.errors import InvalidId
from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.database.mongodb_initiator import rooms_collection, gfs

# Delete a file in a room
def delete_file(fileID, roomCode):
    try:
        file = gfs.find_one({'_id': ObjectId(fileID)})
        if not file:
            print(f'Error in delete_file(). File with fileID [{fileID}] does not exist in database.')
            return
    except InvalidId:
        print(f'Error in delete_file(). fileID [{fileID}] is invalid.')
                
    # Test if given roomCode is in invalid format
    if not room_code_exists_in_collection(roomCode):
        print(f'Error in delete_file(). roomCode [{roomCode}] is invalid.')
        return
    
    if file.metadata['roomCode'] != roomCode:
        print(f'Error in delete_file(). File with fileID [{fileID}] does not exist in roomCode [{roomCode}].')
        return 
    
    # Delete the file, indicated by the fileID, from the database
    gfs.delete(ObjectId(fileID))
    # Remove the filename, indicated by the fileID, from 'fileList' of this room    
    rooms_collection.update_one(
        {'roomCode': roomCode},
        {'$pull': {'fileList': {'fileID': ObjectId(fileID)}}}
    )
    print(f'Successfully deleted file with fileID [{fileID}] in room [{roomCode}].')
    return

# Delete all files in a room
def delete_all_files(roomCode):
    # Use roomCode to get all fileIDs of the room, then use the fileIDs to delete all files
    try:
        files = gfs.find({'metadata.roomCode': roomCode})
    except InvalidId:
        print(f'Error in delete_all_files(). roomCode [{roomCode}] is invalid')
        return
    
    if not files.alive:
        print(f'There are no existing files in room [{roomCode}].')
        return
    for file in files:
        print(f'FileID to be deleted: [{file._id}]')
        delete_file(file._id, roomCode)
    print(f'Successfully deleted all files from room [{roomCode}].')
    return
