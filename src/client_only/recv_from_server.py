# recv_from_server.py

# Used to import files from the 'general' folder
import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1]
sys.path.append(str(src_folder))

import pickle
from general.file_transmission import *
from general.message import (get_prefix_and_content, rstrip_message, 
                             recv_decoded_content)

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

            match prefix:
                case 0: # operation message
                    print()
                case 1: # normal message
                    msgContent = rstrip_message(msgContent)
                    print(msgContent.decode() + '\n')
                case 2: # file-download request initiated by client
                    print(f'type prefix: [{typePrefix}]')
                    print(f'msgContent: [{msgContent}]')
                    filepath = rstrip_message(msgContent).decode()
                    print(f'filepath: [{filepath}]')
                    recv_file_from_server(client, filepath, 
                                         chunkSize, maxFileSize, extList)
                case 4: 
                    response = pickle.loads(msgContent)
                    if type(response) == str and response == 'INVALID':
                        print('Response from server: Invalid display history request.\n')
                    else:    
                        print(response, '\n')
                case 5: 
                    response = msgContent.decode()
                    print(response+'\n')
                case _: # invalid prefix
                    print(f'Received invalid prefix: [{typePrefix}].')
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
        filename, filesize = split_metadata(metadataBytes)
        
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
        recv_file(filename, filepath, filesize, client, chunkSize,
                 'server')
        
        display_rule()
    elif response == 'file_not_found':
        print('Stopped receiving file.')
        display_rule()
    else:
        print(f'Received invalid response from server: [{response}]',
              f'when receiving file.')
