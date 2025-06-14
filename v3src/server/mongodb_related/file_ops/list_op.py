# list_op.py

from bson import ObjectId
from bson.errors import InvalidId

from v3src.server.mongodb_related.file_ops.general_op import roomCode_to_roomID
from v3src.server.mongodb_related.mongodb_initiator import gfs

# List all files in a room
def get_file_history(roomCode):
    roomID = roomCode_to_roomID(roomCode)
    try:
        room_id = ObjectId(roomID)  # Validates the format of roomID
    except InvalidId:
        print(f'Error in get_file_history(). roomID [{roomID}] is invalid')
        return 
    
    # Find all files of given room
    files = gfs.find({'metadata.roomID': roomID})
    if not files.alive:
        print(f'There are no existing files in room [{roomID}].')
        return
    
    return [file.filename for file in files]

def get_fileID(filename, roomCode):
    roomID = roomCode_to_roomID(roomCode)
    print(f'roomID: {roomID}')
    
    try:
        room_id = ObjectId(roomID)  # Validates the format of roomID
    except InvalidId:
        print(f'Error in get_file_history(). roomID [{roomID}] is invalid')
        return None
    
    files = gfs.find({
        'filename': filename,
        'metadata.roomID': roomID
    })
    file_ids = [file._id for file in files]
    if not file_ids:
        print(f'⚠️ No file found with filename [{filename}] in roomID [{roomID}]')
        return None
    return file_ids[0]
