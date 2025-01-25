# handle_download_request.py

from general.file_transmission import (check_if_filesize_is_valid,
                                      create_metadata,
                                      find_file_in_directory, 
                                      get_directory_and_filename,
                                      send_file, send_metadata,
                                      get_extension_from_filename,
                                      check_if_filename_has_valid_extension)
from general.message import send_msg_with_prefix

def handle_download_request(client, address, msgContent, 
                            chunkSize, maxFileSize, extList):
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
        send_file_to_client(client, filepath, chunkSize, maxFileSize, extList)
    return

def send_file_to_client(client, filepath, chunkSize, maxFileSize, extList):
    # Create and send metadata to client
    filename, filesize = create_metadata(filepath)
    
    send_metadata(client, filename, filesize)
    
    # Stop sending file if filesize is greater than MAX_FILE_SIZE
    if not check_if_filesize_is_valid(filesize, maxFileSize):
        print('Stopped sending file.\n')
        return
    
    # Stop sending file if file extension is not in extList
    extension = get_extension_from_filename(filename)
    if not check_if_filename_has_valid_extension(extension, extList):
        print('Stopped sending file.')
        return 
       
    # Send the whole file to client
    send_file(filepath, filename, client, 
             chunkSize, client.getpeername())
    return
