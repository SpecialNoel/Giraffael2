# handle_upload_request.py

import json
from general.file_transmission import (check_if_filesize_is_too_large,
                                      check_metadata_format,
                                      recv_file, split_metadata)
from general.message import get_prefix_and_content

def handle_upload_request(client, address, chunkSize, maxFileSize):
    print(f'client [{address}] is uploading a file.\n')
    
    # Receive metadata from client
    msg = client.recv(chunkSize)
    prefix, metadataBytes = get_prefix_and_content(msg)
    
    # Obtain metadata
    metadata_json = metadataBytes.decode('utf-8')
    metadata = json.loads(metadata_json)
    print(f'Metadata: [{metadata}].')
    if not check_metadata_format(metadata):
        return
    
    # Split the metadata of the file received from client
    filename, filesize = split_metadata(metadataBytes)
    
    # Stop receiving file if filesize is greater than MAX_FILE_SIZE
    if check_if_filesize_is_too_large(filesize, maxFileSize):
        print('Stopped receiving file.\n')
        return
    
    filepath = 'received_files'

    # Receive the whole file from client
    recv_file(filename, filepath, filesize, client, 
             chunkSize, client.getpeername())
    return
