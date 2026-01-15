# upload_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from mongodb_initiator import rooms_collection, gfs
src_folder = Path(__file__).resolve().parents[3] # grand-grandparent level
sys.path.append(str(src_folder))
from general.file_transmission import check_if_file_exists
from file_ops.general_op import check_file_existence_in_room, roomCode_to_roomID

import os
from bson import ObjectId
from bson.errors import InvalidId


# Upload file to a room
def upload_file(filepath, roomCode):    
    # Generate a unique filename to avoid uploading a file with a duplicated filename
    #   as existing files in given room
    # Note: roomID used here will be in correct format as we'll check it before executing here
    def generate_filename_with_unique_postfix(filenameWithExt, roomID):
        counter = 1
        filename, extension = os.path.splitext(filenameWithExt)
        temp_filename = filenameWithExt
        # If there is a file with the same filename stored in current room, try a new postfix
        while check_file_existence_in_room(temp_filename, roomID):
            temp_filename = f'{filename}_{counter}{extension}'
            counter += 1
        return temp_filename
    
    # Check if filepath is valid here
    print(f'Filepath: [{filepath}]')
    if not check_if_file_exists(filepath):
        print(f'Error in upload_file(). Filepath [{filepath}] is invalid.')
        return -1
    
    roomID = roomCode_to_roomID(roomCode)
    
    # Find the given room
    room = None
    try:
        room = rooms_collection.find_one(
            {'_id': ObjectId(roomID)}
        )
    except InvalidId:
        print(f'Error in upload_file(). roomID [{roomID}] is invalid.')
        return -1
    
    if not room:
        print(f'Error in upload_file(). Room with roomID [{roomID}] does not exist.')
        return -1
    
    # Handle name of the file, if it is not unique
    nameOfFile=filepath.split('/')[-1]
    if check_file_existence_in_room(nameOfFile, roomID):
        nameOfFile = generate_filename_with_unique_postfix(nameOfFile, roomID)
    
    # Store the file along with its name and metadata to the database
    with open(filepath, 'rb') as f:
        fileID = gfs.put(
            f,
            filename=nameOfFile,
            metadata={'roomID': roomID}
        )
    # Update the fileList of the room
    rooms_collection.update_one(
        {'_id': ObjectId(roomID)},
        {'$push': {'fileList': {
            'fileID': fileID,
            'filename': nameOfFile
        }}}
    )
    print(f'Uploaded file [{nameOfFile}] with fileID [{fileID}] to room [{roomID}].')
    return fileID
