# handle_download_request.py

import os
import time
from general.file_transmission import (check_if_filesize_is_valid,
                                      create_metadata,
                                      get_directory_and_filename,
                                      send_file, send_metadata,
                                      get_extension_from_filename,
                                      check_if_filename_has_valid_extension)
from general.message import send_msg_with_prefix
from server_only.mongodb_related.file_ops.list_op import get_file_history, get_fileID
from server_only.mongodb_related.file_ops.download_op import download_file

def handle_download_request(clientObj, room, msgContent, 
                            chunkSize, maxFileSize, extList):
    address = clientObj.get_address()
    client = clientObj.get_socket()
    roomCode = room.get_room_code()
    
    # Received file-download request
    print(f'client [{address}] is downloading a file.\n')

    clientDir, filename = get_directory_and_filename(msgContent)
    print(f'clientFilepath: [{clientDir}]')
    print(f'filename: [{filename}]')

    # Inform the client to get ready to receive server response
    send_msg_with_prefix(client, clientDir, 2)
    print('Sent clientFilepath to client.')

    # Try finding the requested file on server
    print(f'Searching requested file in room: [{roomCode}].')
    fileList = get_file_history(roomCode)
    print(f'fileList: {fileList}')
    
    if filename not in fileList:
        # Filename does not exist in room
        print(f'File not found in room [{roomCode}].')
        # Inform client about this
        send_msg_with_prefix(client, 'file_not_found', 0)
        print('Sent response on finding the requested file to client.')
    else:
        # Filename exists in room
        print(f'File found in room [{roomCode}].')
        # Inform client about this
        send_msg_with_prefix(client, 'file_exists', 0)
        print('Sent response on finding the requested file to client.')
        
        # Wait for 1 second before sending the metadata of the file
        # This is needed to solve problem where client receives both 
        #   the response on finding the requested file and the metadata 
        #   from only one recv(chunkSize)
        time.sleep(1)
                
        # Send file to client
        send_file_to_client(client, address, roomCode, filename,
                           chunkSize, maxFileSize, extList)
    return

def send_file_to_client(client, address, roomCode, inputFilename,
                       chunkSize, maxFileSize, extList):
    def save_file_from_database_to_file_buffer_folder_temporary(fileID, roomCode):
        def find_file_buffer_folder():
            startDir = os.path.abspath('.')
            targetFolder = 'file_buffer_folder'
            for root, dirs, files in os.walk(startDir):
                if targetFolder in dirs:
                    return os.path.join(root, targetFolder)
            return None
        
        savepath = download_file(fileID, roomCode, find_file_buffer_folder())
        return savepath
    
    def remove_file_from_file_buffer_folder(filepath):
        if os.path.isfile(filepath):
            os.remove(filepath)
            print(f'File [{filepath}] deleted.')
        else:
            print(f'Error in remove_file_from_file_buffer_folder: File [{filepath}] not found.')
        return 
    
    # Step 1: Query the file from database to local file_buffer_folder first
    fileID = get_fileID(inputFilename, roomCode)
    filepath = save_file_from_database_to_file_buffer_folder_temporary(fileID, roomCode)
    
    # Step 2: Create and send metadata to client
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
       
    # Step 3: Send the file stored in the local file_buffer_folder to client
    send_file(filepath, filename, client, chunkSize, address)
    
    # Step 4: Remove the file stored in the local file_buffer_folder
    remove_file_from_file_buffer_folder(filepath)
    return
