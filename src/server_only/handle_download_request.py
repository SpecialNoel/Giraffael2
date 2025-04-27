# handle_download_request.py

import time
from general.file_transmission import (check_if_filesize_is_valid,
                                      create_metadata,
                                      find_file_in_directory, 
                                      get_directory_and_filename,
                                      send_file, send_metadata,
                                      get_extension_from_filename,
                                      check_if_filename_has_valid_extension)
from general.message import send_msg_with_prefix

def handle_download_request(client, address, room, roomCode, msgContent, 
                            chunkSize, maxFileSize, extList):
    # Received file-download request
    print(f'client [{address}] is downloading a file.\n')

    clientDir, filename = get_directory_and_filename(msgContent)
    print(f'clientFilepath: [{clientDir}]')
    print(f'filename: [{filename}]')

    # Inform the client to get ready to receive server response
    send_msg_with_prefix(client, clientDir, 2)
    print('Sent clientFilepath to client.')

    # Try finding the requested file on server
    directory = room.get_fullpath()
    print(f'Searching requested file in directory: [{directory}].')
    filepath = find_file_in_directory(filename, roomCode, directory)

    if filepath == None:
        # Filename does not exist in directory
        print(f'File not found in [{directory}].')
        # Inform client about this
        send_msg_with_prefix(client, 'file_not_found', 0)
        print('Sent response on finding the requested file to client.')
    else:
        # Filename exists in directory
        print(f'File found in [{directory}].')
        # Inform client about this
        send_msg_with_prefix(client, 'file_exists', 0) # ------------------------ Client has received this
        print('Sent response on finding the requested file to client.')
        
        # Wait for 1 second before sending the metadata of the file
        # This is needed to solve problem where client receives both 
        #   the response on finding the requested file and the metadata 
        #   from only one recv(chunkSize)
        time.sleep(1)
        
        # Send file to client
        send_file_to_client(client, address, filepath, chunkSize, maxFileSize, extList)
    return

def send_file_to_client(client, address, filepath, chunkSize, maxFileSize, extList):
    # Create and send metadata to client
    filename, filesize, hashedFileContent = create_metadata(filepath)
    
    send_metadata(client, filename, filesize, hashedFileContent)
    print('Sent metadata of the requested file to client.')
    
    # Stop sending file if filesize is greater than MAX_FILE_SIZE
    if not check_if_filesize_is_valid(filesize, maxFileSize):
        print('Stopped sending file.\n')
        return
    print('Filesize is valid.')
    
    # Stop sending file if file extension is not in extList
    extension = get_extension_from_filename(filename)
    if not check_if_filename_has_valid_extension(extension, extList):
        print('Stopped sending file.')
        return
    print('File extension is valid.')
    
    # Wait for 1 second before sending the whole file
    # This is needed to solve problem where client receives both 
    #   the metadata and the file itself from only one recv(chunkSize)
    time.sleep(1)
       
    # Send the whole file to client
    send_file(filepath, filename, client, chunkSize, address)
    return
