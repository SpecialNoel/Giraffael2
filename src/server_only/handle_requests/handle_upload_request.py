# handle_upload_request.py

import json
import os
from general.file_transmission import (check_if_filesize_is_valid,
                                      check_metadata_format,
                                      recv_file, split_metadata,
                                      get_extension_from_filename,
                                      check_if_filename_has_valid_extension)
from general.message import get_prefix_and_content
from server_only.mongodb_related.file_ops.upload_op import upload_file

def handle_upload_request(clientObj, roomCode, chunkSize, 
                          maxFileSize, extList):
    def find_file_buffer_folder():
        startDir = os.path.abspath('.')
        targetFolder = 'file_buffer_folder'
        for root, dirs, files in os.walk(startDir):
            if targetFolder in dirs:
                return os.path.join(root, targetFolder)
        return None
        
    def remove_file_from_file_buffer_folder(filepath):
        if os.path.isfile(filepath):
            os.remove(filepath)
            print(f'File [{filepath}] deleted.')
        else:
            print(f'Error in remove_file_from_file_buffer_folder: File [{filepath}] not found.')
        return 

    address = clientObj.get_address()
    client = clientObj.get_socket()
    
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
    
    # Receive the whole file from client
    filepath = recv_file(filename, find_file_buffer_folder(), filesize, 
                       hashedFileContent, client, chunkSize, address)
    
    # Update fileList in the room in database
    if filepath:
        upload_file(filepath, roomCode)
        remove_file_from_file_buffer_folder(filepath)
    else:
        print(f'Failed to add [{filename}] to room [{roomCode}].')
    return
