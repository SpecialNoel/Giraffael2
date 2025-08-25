# list_op.py

from bson import ObjectId
from bson.errors import InvalidId

from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.database.mongodb_initiator import gfs

# List all files in a room
def get_file_history(roomCode):
    if not room_code_exists_in_collection(roomCode):
        print(f'Error in get_file_history(). roomCode [{roomCode}] is invalid')
        return 
    
    # Find all files of given room
    files = gfs.find({'metadata.roomCode': roomCode})
    if not files.alive:
        print(f'There are no existing files in room [{roomCode}].')
        return
    
    return [file.filename for file in files]

def get_fileID(filename, roomCode):
    if not room_code_exists_in_collection(roomCode):
        print(f'Error in get_file_history(). roomCode [{roomCode}] is invalid')
        return None
    
    files = gfs.find({
        'filename': filename,
        'metadata.roomCode': roomCode
    })
    file_ids = [file._id for file in files]
    if not file_ids:
        print(f'⚠️ No file found with filename [{filename}] in roomCode [{roomCode}]')
        return None
    return file_ids[0]
