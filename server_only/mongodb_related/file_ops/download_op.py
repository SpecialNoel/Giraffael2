# download_op.py

import os
from server_only.mongodb_related.msg_ops.general_op import room_code_to_room_id
from server_only.mongodb_related.mongodb_initiator import rooms_collection, gfs
from general.file_transmission import get_file_path_without_duplication
from bson import ObjectId
from bson.errors import InvalidId
from gridfs.errors import NoFile

# Download file from a room
def download_file(file_id, room_code, save_dir):
    try: 
        file = gfs.get(ObjectId(file_id))
    except InvalidId:
        print(f'Error in download_file(). FileID [{file_id}] is invalid.')
        return
    except NoFile: 
        print(f'Error in download_file(). File with file_id [{file_id}] does not exist in database.')
        return
    
    room_id = room_code_to_room_id(room_code)
    
    # Test if given room_id is in invalid format
    try:
        room = rooms_collection.find_one(
            {'_id': ObjectId(room_id)}
        )
    except InvalidId:
        print(f'Error in download_file(). room_id [{room_id}] is invalid.')
        return
    
    # Test if the file is in database, but not in the given room 
    if file.metadata['room_id'] != room_id:
        print(f'Error in download_file(). File with file_id [{file_id}] does not exist in room [{room_id}].')
        return 
    
    # Start downloading the file
    filename = file.filename 
    save_path = os.path.join(save_dir, filename)
    # Add a unique postfix to the filename of the save_path to avoid duplicated filename inside user-end folder.
    save_path = get_file_path_without_duplication(save_path)
    with open(save_path, 'wb') as f:
        f.write(file.read())
    print(f'Downloaded file with file_id [{file_id}] from room [{room_id}], stored at [{save_path}].')
    return