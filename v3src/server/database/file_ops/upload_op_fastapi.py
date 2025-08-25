# upload_op_fastapi.py

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import File, UploadFile
from v3src.server.database.mongodb_initiator import rooms_collection, gfs

# Upload file to a room using fastapi
def upload_file_with_fastapi(roomCode: str, file: UploadFile = File(...)):        
    # # Find the given room
    room = None
    try:
        room = rooms_collection.find_one(
            {'roomCode': roomCode}
        )
    except InvalidId:
        print(f'Error in upload_file(). roomCode [{roomCode}] is invalid.')
        return -1
    
    if not room:
        print(f'Error in upload_file(). Room with roomCode [{roomCode}] does not exist.')
        return -1
    
    contents = file.file.read()
    fileID = gfs.put(contents, 
                     filename=file.filename, 
                     metadata={'roomCode': roomCode})
        # Update the fileList of the room
    rooms_collection.update_one(
        {'roomCode': roomCode},
        {'$push': {'fileList': {
            'fileID': fileID,
            'filename': file.filename
        }}}
    )
    print(f'Uploaded file [{file.filename}] with fileID [{fileID}] to room [{roomCode}].')
    return fileID
