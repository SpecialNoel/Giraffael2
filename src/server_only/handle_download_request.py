# handle_download_request.py

from general.file_transmission import (create_metadata,
                                      find_file_in_directory, 
                                      get_directory_and_filename,
                                      send_file, send_metadata)
from general.message import send_msg_with_prefix

def handle_download_request(client, address, msgContent, chunkSize):
    # Received file-download request
    print(f'client [{address}] is downloading a file.\n')
    
    clientDir, filename = get_directory_and_filename(msgContent)
    print(f'clientFilepath: [{clientDir}]')
    
    # Inform the client to get ready to receive server response
    send_msg_with_prefix(client, clientDir, 2)

    # Try finding the requested file on server
    filepath = find_file_in_directory(filename, 'test_files')
    
    if filepath == None:
        # Filename found in test_files folder
        send_msg_with_prefix(client, 'file_not_found', 0)
    else:
        # Filename does not exist in test_files folder
        send_msg_with_prefix(client, 'file_exists', 0)
        # Send file to client
        send_file_to_client(client, filepath, chunkSize)
    return

def send_file_to_client(client, filepath, chunkSize):
    # Create and send metadata to client
    filename, filesize = create_metadata(filepath)
    send_metadata(client, filename, filesize)
   
    # Send the whole file to client
    send_file(filepath, filename, client, 
             chunkSize, client.getpeername())
    return
