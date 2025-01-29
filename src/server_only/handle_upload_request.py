# handle_upload_request.py

import json
import os
from general.file_transmission import (check_if_filesize_is_valid,
                                      check_metadata_format,
                                      recv_file, split_metadata,
                                      get_extension_from_filename,
                                      check_if_filename_has_valid_extension)
from general.message import get_prefix_and_content

def handle_upload_request(client, address, room, roomCode, chunkSize, 
                          maxFileSize, extList):
    print(f'client [{address}] is uploading a file.\n')
    
    # Receive metadata from client
    msg = client.recv(chunkSize)
    prefix, metadataBytes = get_prefix_and_content(msg)
    
    # Obtain metadata
    metadata_json = metadataBytes.decode()
    metadata = json.loads(metadata_json)
    print(f'Metadata: [{metadata}].')
    if not check_metadata_format(metadata):
        return
    
    # Split the metadata of the file received from client
    filename, filesize, hashedFileContent = split_metadata(metadataBytes)
    
    # Stop receiving file if filesize is greater than MAX_FILE_SIZE
    if not check_if_filesize_is_valid(filesize, maxFileSize):
        print('Stopped receiving file.\n')
        return
    
    # Stop receiving file if file extension is not in extList
    extension = get_extension_from_filename(filename)
    if not check_if_filename_has_valid_extension(extension, extList):
        print('Stopped receiving file.')
        return 
    
    filepath = 'rooms' + os.sep + roomCode

    # Receive the whole file from client
    fileSaved = recv_file(filename, filepath, filesize, hashedFileContent,
                        client, chunkSize, address)
    
    # Update '__storedFiles' in the room client is in
    
    if fileSaved:
        room.add_files_to_stored_files(filename)
    else:
        print(f'Failed to add [{filename}] to room [{roomCode}].')
    print(f'\nCurrent files in room [{roomCode}]: {room.get_stored_files()}\n.')
    return
