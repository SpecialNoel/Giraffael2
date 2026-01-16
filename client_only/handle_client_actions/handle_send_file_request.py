# handle_send_file_request.py

import time
from general.file_transmission import *
from general.message import send_msg_with_prefix

def handle_send_file_request(client, chunk_size, max_file_size, ext_list):    
    print('Type in file path of the file you want to send.')
    print('OR, type <exit> to stop sending file.\n')
    file_path = rstrip_message(input())
    
    # Client does not want to send the file anymore
    if file_path.lower() == 'exit':
        print('Stopped sending file.')
        display_rule()
        return
    
    # Check if file path is valid
    file_path = get_valid_file_path(file_path)
    
    if file_path == None:
        print('Stopped sending file.')
        display_rule()
        return
    
    # Send the file to server
    send_file_to_server(client, file_path, chunk_size, max_file_size, ext_list)
    return

def send_file_to_server(client, file_path, chunk_size, max_file_size, ext_list):
    # Create and send metadata to server
    filename, file_size, hashed_file_content = create_metadata(file_path)
    
    # Stop sending file if file_size is greater than MAX_FILE_SIZE
    if not check_if_file_size_is_valid(file_size, max_file_size):
        print('Stopped sending file.')
        display_rule()
        return
    
    # Stop sending file if file extension is not in ext_list
    extension = get_extension_from_filename(filename)
    if not check_if_filename_has_valid_extension(extension, ext_list):
        print('Stopped receiving file.')
        display_rule()
        return 
    
    # Inform server that this client wants to send a file
    send_msg_with_prefix(client, '', 2)
    
    # Send metadata of the file to server
    send_metadata(client, filename, file_size, hashed_file_content)
    
    # Wait for 1 second before sending the whole file
    # This is needed to solve problem where server receives both 
    #   the metadata and the file itself from only one recv(chunk_size)
    time.sleep(1)
    
    # Send the whole file to server
    send_file(file_path, filename, client, chunk_size, 'server')
    
    display_rule()
    return
