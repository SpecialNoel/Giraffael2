# upload_op.py

import os
from bson import ObjectId
from bson.errors import InvalidId
from v3src.server.mongo_db.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.mongo_db.file_ops.general_op import check_file_existence_in_room
from v3src.server.mongo_db.mongodb_initiator import rooms_collection, gfs

# Upload file to a room
def upload_file(filepath, roomCode):    
    # Generate a unique filename to avoid uploading a file with a duplicated filename
    #   as existing files in given room
    # Note: roomCode used here will be in correct format as we'll check it before executing here
    def generate_filename_with_unique_postfix(filenameWithExt, roomCode):
        counter = 1
        filename, extension = os.path.splitext(filenameWithExt)
        temp_filename = filenameWithExt
        # If there is a file with the same filename stored in current room, try a new postfix
        while check_file_existence_in_room(temp_filename, roomCode):
            temp_filename = f'{filename}_{counter}{extension}'
            counter += 1
        return temp_filename
    
    # Check if filepath is valid here
    print(f'Filepath: [{filepath}]')
    if not check_if_file_exists(filepath):
        print(f'Error in upload_file(). Filepath [{filepath}] is invalid.')
        return -1
        
    # Find the given room
    room = None
    try:
        room = rooms_collection.find_one(
            {'roomCode': roomCode}
        )
    except InvalidId:
        print(f'Error in upload_file(). Room code [{roomCode}] is invalid.')
        return -1
    
    if not room:
        print(f'Error in upload_file(). Room code [{roomCode}] does not exist.')
        return -1
    
    # Handle name of the file, if it is not unique
    nameOfFile = os.path.basename(filepath)
    if check_file_existence_in_room(nameOfFile, roomCode):
        nameOfFile = generate_filename_with_unique_postfix(nameOfFile, roomCode)
    
    # Store the file along with its name and metadata to the database
    with open(filepath, 'rb') as f:
        fileID = gfs.put(
            f,
            filename=nameOfFile,
            metadata={'roomCode': roomCode}
        )
    # Update the fileList of the room
    rooms_collection.update_one(
        {'roomCode': roomCode},
        {'$push': {'fileList': {
            'fileID': fileID,
            'filename': nameOfFile
        }}}
    )
    print(f'Uploaded file [{nameOfFile}] with fileID [{fileID}] to room [{roomCode}].')
    return fileID
