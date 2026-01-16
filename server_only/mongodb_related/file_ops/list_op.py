# list_op.py

from server_only.mongodb_related.mongodb_initiator import gfs
from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from bson import ObjectId
from bson.errors import InvalidId

# List all files in a room
def list_files(room_code):
    room_id = room_code_to_room_id(room_code)
    try:
        room_id = ObjectId(room_id)  # Validates the format of room_id
    except InvalidId:
        print(f'Error in list_files(). room_id [{room_id}] is invalid')
        return 
    
    # Find all files of given room
    files = gfs.find({'metadata.room_id': room_id})
    if not files.alive:
        print(f'There are no existing files in room [{room_id}].')
        return
    
    print(f'Files stored in room [{room_id}]:')
    for file in files:
        print(f'[{file.filename}]')
    return
