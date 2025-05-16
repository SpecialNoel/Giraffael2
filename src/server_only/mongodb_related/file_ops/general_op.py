# general_op.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1] # parent level
sys.path.append(str(src_folder))
from mongodb_initiator import rooms_collection, gfs

from bson.errors import InvalidId

'''
  File structure:      (file_content, filename, metadata: {'roomID'})
  File List structure: {{fileID, filename}, ...}
  # Note1: fileID for operations in backend; filename for better user experience. 
  # Note2: filename is unique per room. fileID is unique globally.
'''

# Get the file in a room by filename
def get_file_by_filename_and_roomID(filename, roomID):
    file = None
    try:
        file = gfs.find_one({
            'filename': filename,
            'metadata.roomID': roomID
        })
    except InvalidId:
        print('Error in get_file_by_filename_and_roomID(). '
              f'roomID [{roomID}] is invalid.')
    return file

# Check if the target file is stored in a room by filename
def check_file_existence_in_room(filename, roomID):
    return get_file_by_filename_and_roomID(filename, roomID) is not None

# Get the corresponding fileID with given filename in a room
def get_fileID_by_filename_and_roomID(filename, roomID):
    file = get_file_by_filename_and_roomID(filename, roomID)
    if file is None:
        print('Error in get_fileID_by_filename_and_roomID(). '
              f'File with filename [{filename}] cannot be found in room [{roomID}].')
        return ''
    return file._id
    
# get roomID with the roomCode of a room, if any
def roomCode_to_roomID(roomCode):
    room = rooms_collection.find_one(
        {'roomCode': roomCode}
    )   
    return room['_id'] if room is not None else None
