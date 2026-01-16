# handle_download_request.py

import time
from general.file_transmission import (check_if_file_size_is_valid,
                                      create_metadata,
                                      get_file_path, 
                                      get_directory_and_filename,
                                      send_file, send_metadata,
                                      get_extension_from_filename,
                                      check_if_filename_has_valid_extension)
from general.message import send_msg_with_prefix
from server_only.mongodb_related.file_ops.list_op import list_files
from server_only.mongodb_related.file_ops.download_op import download_file

def handle_download_request(client, address, room, room_code, msg_content, 
                            chunk_size, max_file_size, ext_list):
    # Received file-download request
    print(f'client [{address}] is downloading a file.\n')

    client_dir, filename = get_directory_and_filename(msg_content)
    print(f'client file path: [{client_dir}]')
    print(f'filename: [{filename}]')

    # Inform the client to get ready to receive server response
    send_msg_with_prefix(client, client_dir, 2)
    print('Sent client file path to client.')

    # Try finding the requested file on server
    directory = room.get_full_path()
    print(f'Searching requested file in directory: [{directory}].')
    file_path = get_file_path(filename, room_code, directory)
    
    # list files to check (database op)
    
    

    if file_path == None:
        # Filename does not exist in directory
        print(f'File not found in [{directory}].') 
        # Inform client about this
        send_msg_with_prefix(client, 'file_not_found', 0)
        print('Sent response on finding the requested file to client.')
    else:
        # Filename exists in directory
        print(f'File found in [{directory}].')
        # Inform client about this
        send_msg_with_prefix(client, 'file_exists', 0)
        print('Sent response on finding the requested file to client.')
        
        # Wait for 1 second before sending the metadata of the file
        # This is needed to solve problem where client receives both 
        #   the response on finding the requested file and the metadata 
        #   from only one recv(chunk_size)
        time.sleep(1)
        
        # Send file to client
        send_file_to_client(client, address, file_path, chunk_size, max_file_size, ext_list)
    return

def send_file_to_client(client, address, file_path, chunk_size, max_file_size, ext_list):
    # Create and send metadata to client
    filename, file_size, hashed_file_content = create_metadata(file_path)
    
    send_metadata(client, filename, file_size, hashed_file_content)
    print('Sent metadata of the requested file to client.')
    
    # Stop sending file if file_size is greater than MAX_FILE_SIZE
    if not check_if_file_size_is_valid(file_size, max_file_size):
        print('Stopped sending file.\n')
        return
    print('Filesize is valid.')
    
    # Stop sending file if file extension is not in ext_list
    extension = get_extension_from_filename(filename)
    if not check_if_filename_has_valid_extension(extension, ext_list):
        print('Stopped sending file.')
        return
    print('File extension is valid.')
    
    # Wait for 1 second before sending the whole file
    # This is needed to solve problem where client receives both 
    #   the metadata and the file itself from only one recv(chunk_size)
    time.sleep(1)
       
    # Send the whole file to client
    send_file(file_path, filename, client, chunk_size, address)
    
    # download file (database op)
    return
