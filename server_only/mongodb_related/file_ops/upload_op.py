# upload_op.py

import os
from server_only.mongodb_related.mongodb_initiator import rooms_collection, gfs
from general.file_transmission import check_if_file_exists
from server_only.mongodb_related.file_ops.general_op import check_file_existence_in_room, room_code_to_room_id
from bson import ObjectId
from bson.errors import InvalidId

# Upload file to a room
def upload_file(file_path, room_code):    
    # Generate a unique filename to avoid uploading a file with a duplicated filename
    #   as existing files in given room
    # Note: room_id used here will be in correct format as we'll check it before executing here
    def generate_filename_with_unique_postfix(filename_with_ext, room_id):
        counter = 1
        filename, extension = os.path.splitext(filename_with_ext)
        temp_filename = filename_with_ext
        # If there is a file with the same filename stored in current room, try a new postfix
        while check_file_existence_in_room(temp_filename, room_id):
            temp_filename = f'{filename}_{counter}{extension}'
            counter += 1
        return temp_filename
    
    # Check if file path is valid here
    print(f'File path: [{file_path}]')
    if not check_if_file_exists(file_path):
        print(f'Error in upload_file(). File path [{file_path}] is invalid.')
        return -1
    
    room_id = room_code_to_room_id(room_code)
    
    # Find the given room
    room = None
    try:
        room = rooms_collection.find_one(
            {'_id': ObjectId(room_id)}
        )
    except InvalidId:
        print(f'Error in upload_file(). room_id [{room_id}] is invalid.')
        return -1
    
    if not room:
        print(f'Error in upload_file(). Room with room_id [{room_id}] does not exist.')
        return -1
    
    # Handle name of the file, if it is not unique
    filename=file_path.split('/')[-1]
    if check_file_existence_in_room(filename, room_id):
        filename = generate_filename_with_unique_postfix(filename, room_id)
    
    # Store the file along with its name and metadata to the database
    with open(file_path, 'rb') as f:
        file_id = gfs.put(
            f,
            filename=filename,
            metadata={'room_id': room_id}
        )
    # Update the file_list of the room
    rooms_collection.update_one(
        {'_id': ObjectId(room_id)},
        {'$push': {'file_list': {
            'file_id': file_id,
            'filename': filename
        }}}
    )
    print(f'Uploaded file [{filename}] with file_id [{file_id}] to room [{room_id}].')
    return file_id
