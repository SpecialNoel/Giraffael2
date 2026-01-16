# handle_upload_request.py

import json
from general.file_transmission import (check_if_file_size_is_valid,
                                      check_metadata_format,
                                      recv_file, split_metadata,
                                      get_extension_from_filename,
                                      check_if_filename_has_valid_extension)
from general.message import get_prefix_and_content
from server_only.mongodb_related.file_ops.upload_op import upload_file

def handle_upload_request(client, address, room, room_code, chunk_size, 
                          max_file_size, ext_list):
    print(f'client [{address}] is uploading a file.\n')
    
    # Receive metadata from client
    msg = client.recv(chunk_size)
    prefix, metadata_bytes = get_prefix_and_content(msg)
    
    # Obtain metadata 
    metadata_json = metadata_bytes.decode() 
    metadata = json.loads(metadata_json)
    print(f'Metadata: [{metadata}].')
    if not check_metadata_format(metadata):
        return 
    
    # Split the metadata of the file received from client
    filename, file_size, hashed_file_content = split_metadata(metadata_bytes)
    
    # Stop receiving file if file_size is greater than MAX_FILE_SIZE
    if not check_if_file_size_is_valid(file_size, max_file_size):
        print('Stopped receiving file.\n')
        return
    
    # Stop receiving file if file extension is not in ext_list
    extension = get_extension_from_filename(filename)
    if not check_if_filename_has_valid_extension(extension, ext_list):
        print('Stopped receiving file.')
        return 
    
    # Receive the whole file from client
    file_path = recv_file(filename, room.get_full_path(), file_size, 
                        hashed_file_content, client, chunk_size, address)
    
    # Update '__stored_files' in the room client is in
    if file_path:
        room.add_files_to_stored_files(filename)
        upload_file(file_path, room_code)
    else:
        print(f'Failed to add [{filename}] to room [{room_code}].')
    print(f'\nCurrent files in room [{room_code}]: {room.get_stored_files()}\n.')
    return
