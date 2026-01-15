# list_op.py

from server_only.mongodb_related.mongodb_initiator import gfs
from server_only.mongodb_related.msg_ops.general_op import roomCode_to_roomID
from bson import ObjectId
from bson.errors import InvalidId

# List all files in a room
def list_files(roomCode):
    roomID = roomCode_to_roomID(roomCode)
    try:
        room_id = ObjectId(roomID)  # Validates the format of roomID
    except InvalidId:
        print(f'Error in list_files(). roomID [{roomID}] is invalid')
        return 
    
    # Find all files of given room
    files = gfs.find({'metadata.roomID': roomID})
    if not files.alive:
        print(f'There are no existing files in room [{roomID}].')
        return
    
    print(f'Files stored in room [{roomID}]:')
    for file in files:
        print(f'[{file.filename}]')
    return
