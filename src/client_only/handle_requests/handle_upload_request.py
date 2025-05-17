# handle_upload_request.py

import time
from general.file_transmission import *
from general.message import send_msg_with_prefix

def handle_upload_file_request(client, chunkSize, maxFileSize, extList):    
    print('Type in filepath of the file you want to send.')
    print('OR, type <exit> to stop sending file.\n')
    filepath = rstrip_message(input())
    
    # Client does not want to send the file anymore
    if filepath.lower() == 'exit':
        print('Stopped sending file.')
        display_rule()
        return
    
    # Check if filepath is valid
    filepath = get_valid_filepath(filepath)
    
    if filepath == None:
        print('Stopped sending file.')
        display_rule()
        return
    
    # Send the file to server
    upload_file_to_server(client, filepath, chunkSize, maxFileSize, extList)
    return

def upload_file_to_server(client, filepath, chunkSize, maxFileSize, extList):
    # Create and send metadata to server
    filename, filesize, hashedFileContent = create_metadata(filepath)
    
    # Stop sending file if filesize is greater than MAX_FILE_SIZE
    if not check_if_filesize_is_valid(filesize, maxFileSize):
        print('Stopped sending file.')
        display_rule()
        return
    
    # Stop sending file if file extension is not in extList
    extension = get_extension_from_filename(filename)
    if not check_if_filename_has_valid_extension(extension, extList):
        print('Stopped receiving file.')
        display_rule()
        return 
    
    # Inform server that this client wants to send a file
    send_msg_with_prefix(client, '', 2)
    
    # Send metadata of the file to server
    send_metadata(client, filename, filesize, hashedFileContent)
    
    # Wait for 1 second before sending the whole file
    # This is needed to solve problem where server receives both 
    #   the metadata and the file itself from only one recv(chunkSize)
    time.sleep(1)
    
    # Send the whole file to server
    send_file(filepath, filename, client, chunkSize, 'server')
    
    display_rule()
    return
