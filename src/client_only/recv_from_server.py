# recv_from_server.py

# Used to import files from the 'general' folder
import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1]
sys.path.append(str(src_folder))

from general.file_transmission import display_rule, recv_file, split_metadata
from general.message import (get_prefix_and_content, rstrip_message, 
                             recv_decoded_content)

def recv_msg_from_server(client, shutdownEvent, chunkSize):
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
                    recv_file_from_server(client, filepath, chunkSize)
                case _: # invalid prefix
                    print(f'Received invalid prefix: [{typePrefix}].')
        except Exception as e:
            print(f'Error [{e}] occurred when receiving message.')
            break
    client.close() # will be detected by server's 'recv()'
    print('Client receiver thread stopped.')
    return

def recv_file_from_server(client, filepath, chunkSize):
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
