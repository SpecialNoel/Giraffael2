# upload_op_fastapi.py

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import File, UploadFile
from v3src.server.database.file_ops.general_op import roomCode_to_roomID
from v3src.server.database.mongodb_initiator import rooms_collection, gfs

# Upload file to a room using fastapi
def upload_file_with_fastapi(roomCode: str, file: UploadFile = File(...)):    
    roomID = roomCode_to_roomID(roomCode)
    print(f'roomID: {roomID}')    

    # # Find the given room
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
    
    contents = file.file.read()
    fileID = gfs.put(contents, 
                     filename=file.filename, 
                     metadata={'roomID': roomID})
        # Update the fileList of the room
    rooms_collection.update_one(
        {'_id': ObjectId(roomID)},
        {'$push': {'fileList': {
            'fileID': fileID,
            'filename': file.filename
        }}}
    )
    print(f'Uploaded file [{file.filename}] with fileID [{fileID}] to room [{roomID}].')
    return fileID
