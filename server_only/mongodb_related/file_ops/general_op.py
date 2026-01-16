# general_op.py

from server_only.mongodb_related.mongodb_initiator import rooms_collection, gfs
from bson.errors import InvalidId

'''
  File structure:      (file_content, filename, metadata: {'room_id'})
  File List structure: {{file_id, filename}, ...}
  # Note1: file_id for operations in backend; filename for better user experience. 
  # Note2: filename is unique per room. file_id is unique globally.
'''

# Get the file in a room by filename
def get_file_by_filename_and_room_id(filename, room_id):
    file = None
    try:
        file = gfs.find_one({
            'filename': filename,
            'metadata.room_id': room_id
        })
    except InvalidId:
        print('Error in get_file_by_filename_and_room_id(). '
              f'room_id [{room_id}] is invalid.')
    return file

# Check if the target file is stored in a room by filename
def check_file_existence_in_room(filename, room_id):
    return get_file_by_filename_and_room_id(filename, room_id) is not None

# Get the corresponding file_id with given filename in a room
def get_file_id_by_filename_and_room_id(filename, room_id):
    file = get_file_by_filename_and_room_id(filename, room_id)
    if file is None:
        print('Error in get_file_id_by_filename_and_room_id(). '
              f'File with filename [{filename}] cannot be found in room [{room_id}].')
        return ''
    return file._id
    
# get room_id with the room_code of a room, if any
def room_code_to_room_id(room_code):
    room = rooms_collection.find_one(
        {'room_code': room_code}
    )   
    return room['_id'] if room is not None else None
