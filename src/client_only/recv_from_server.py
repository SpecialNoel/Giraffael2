# recv_from_server.py

# Used to import files from the 'general' folder
import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1]
sys.path.append(str(src_folder))
  
import pickle 
from client_only.handle_msg_suggestion import handle_msg_suggestion
from general.file_transmission import *
from general.message import (get_prefix_and_content, rstrip_message, 
                             recv_decoded_content)
 
''' 
def handle_recv_request_with_match(prefix, typePrefix, msgContent, client, 
                                   chunkSize, maxFileSize, extList):
    match prefix:
        case 0: 
            # operation message
            print()
        case 1: 
            # normal message
            msgContent = rstrip_message(msgContent)
            print(msgContent.decode() + '\n')
        case 2: 
            # file-download request initiated by client
            print(f'type prefix: [{typePrefix}]')
            print(f'msgContent: [{msgContent}]')
            filepath = rstrip_message(msgContent).decode()
            print(f'filepath: [{filepath}]')
            recv_file_from_server(client, filepath, 
                                 chunkSize, maxFileSize, extList)
        case 3:
            # file-upload request initiated by client
            # handled in handle_send_file_request.py
            print('file-upload request initiated by client.')
        case 4: 
            # display msg/file history request
            response = pickle.loads(msgContent)
            if type(response) == str and response == 'INVALID':
                print('Response from server: Invalid display history request.\n')
            else:    
                print(response, '\n')
        case 5: 
            # clear msg/file/all history request
            response = msgContent.decode()
            print(response+'\n')
        case 6: 
            # message suggestions generated by OpenAI model
            handle_msg_suggestion(client, msgContent)
        case _: # invalid prefix
            print(f'Received invalid prefix: [{typePrefix}].')
    return
''' 

def handle_recv_request(prefix, typePrefix, msgContent, client, 
                        chunkSize, maxFileSize, extList):
    if prefix == 0: 
        # operation message
        print()
    elif prefix == 1: 
        # normal message
        msgContent = rstrip_message(msgContent)
        print(msgContent.decode() + '\n')
    elif prefix == 2: 
        # file-download request initiated by client
        print(f'type prefix: [{typePrefix}]')
        print(f'msgContent: [{msgContent}]')
        filepath = rstrip_message(msgContent).decode()
        print(f'filepath: [{filepath}]')
        recv_file_from_server(client, filepath, chunkSize, maxFileSize, extList)
    elif prefix == 3:
        # file-upload request initiated by client
        # handled in handle_send_file_request.py
        print('file-upload request initiated by client.')
    elif prefix == 4: 
        # display msg/file history request
        response = pickle.loads(msgContent)
        if type(response) == str and response == 'INVALID':
            print('Response from server: Invalid display history request.\n')
        else:    
            print(response, '\n')
    elif prefix == 5: 
        # clear msg/file/all history request
        response = msgContent.decode()
        print(response+'\n')
    elif prefix == 6: 
        # message suggestions generated by OpenAI model
        handle_msg_suggestion(client, msgContent)
    else: # invalid prefix
        print(f'Received invalid prefix: [{typePrefix}].')
    return

def recv_msg_from_server(client, shutdownEvent, chunkSize, 
                         maxFileSize, extList):
    # Receive message from server
    while not shutdownEvent.is_set(): 
        try:
            msg = client.recv(chunkSize) # 1025 bytes
            
            # Empty message received -> server closed connection
            if not msg:
                print('Server has closed the connection.')
                shutdownEvent.set()
                break 
            
            typePrefix, msgContent = get_prefix_and_content(msg)
            prefix = int.from_bytes(typePrefix, byteorder='big')

            handle_recv_request(prefix, typePrefix, msgContent, client, 
                                chunkSize, maxFileSize, extList)
        except Exception as e:
            print(f'Error [{e}] occurred when receiving message.')
            break 
    client.close() # will be detected by server's 'recv()'
    print('Client receiver thread stopped.')
    return

def recv_file_from_server(client, filepath, chunkSize, maxFileSize, extList):
    # Receive server response for whether server has that file or not
    # If server has it, response should be 'file_exists'
    # Otherwise, response should be 'file_not_found'
    response = recv_decoded_content(client, chunkSize)
    print(f'Received response on file-download from server: {response}')
    if response == 'file_exists':
        # Receive metadata from server
        msg = client.recv(chunkSize)
        prefix, metadataBytes = get_prefix_and_content(msg)
        filename, filesize, hashedFileContent = split_metadata(metadataBytes)
        
        # Stop receiving file if filesize is greater than MAX_FILE_SIZE
        if not check_if_filesize_is_valid(filesize, maxFileSize):
            print('Stopped receiving file.')
            display_rule()
            return 
        
        # Stop receiving file if file extension is not in extList
        extension = get_extension_from_filename(filename)
        if not check_if_filename_has_valid_extension(extension, extList):
            print('Stopped receiving file.')
            display_rule()
            return 
        
        # Receive file from server, and store it on client desired location
        recv_file(filename, filepath, filesize, hashedFileContent, 
                  client, chunkSize, 'server')
        
        display_rule()
    elif response == 'file_not_found':
        print('Stopped receiving file.')
        display_rule()
    else:
        print(f'Received invalid response from server: [{response}]',
              f'when receiving file.')
    return
