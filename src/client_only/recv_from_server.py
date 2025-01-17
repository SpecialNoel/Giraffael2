# recv_from_server.py


# Used to import files from the 'general' folder
import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[1]
sys.path.append(str(src_folder))

from general.file_transmission import (check_metadata_format,
                                      split_metadata, recv_file)
from general.message import rstrip_message, get_prefix_and_content


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
                case 0: # normal message
                    msgContent = rstrip_message(msgContent)
                    print(msgContent.decode() + '\n')
                case 1: # file content
                    # msgContent is metadata of the file
                    recv_file_from_server(msgContent)
                case _: # invalid prefix
                    print(f'Received invalid prefix: {typePrefix}.')
        except Exception as e:
            print(f'Error [{e}] occurred when receiving message.')
            break
    client.close() # will be detected by server's 'recv()'
    print('Client receiver thread stopped.')
    return


def recv_file_from_server(client, msgContent, msgContentSize):
    # Obtain metadata
    metadata = msgContent.decode()
    print(f'Metadata:  {metadata}.')
    if not check_metadata_format(metadata):
        return
            
    # Split the metadata of the file received from server
    filename, filesize = split_metadata(metadata)
    
    # Receive the whole file from server
    recv_file(filename, filesize, client, 
             msgContentSize, 'server')
    return