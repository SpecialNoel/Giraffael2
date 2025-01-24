# handle_client.py

from general.file_transmission import (find_file_in_directory, 
                                      get_filepath_and_filename)
from general.message import (get_prefix_and_content, 
                             rstrip_message,
                             send_msg_with_prefix)
from server_only.remove_client import handle_client_disconnect_request
from server_only.recv_from_client import (handle_client_normal_message,
                                          recv_file_from_client)
from server_only.send_to_client import send_file_to_client

def handle_one_client(shutdownEvent, clientObj, clients, chunkSize,
                      rooms, roomCodes, maxClientCount):
    client = clientObj.get_socket()
    address = clientObj.get_address()
    roomCode = clientObj.get_room_code()
    
    while not shutdownEvent.is_set():
        try:
            msg = client.recv(chunkSize) # 1025 bytes
            typePrefix, msgContent = get_prefix_and_content(msg)
            prefix = int.from_bytes(typePrefix, byteorder='big')
            
            print(f'msg: [{msg}]')
            print(f'Type Prefix: [{typePrefix}]')
            print(f'Content: [{msgContent}]')
            print(f'Prefix: [{prefix}]')

            # Empty message -> client closed connection
            if not msg:
                handle_client_disconnect_request(client, clients, address, 
                                                 rooms, roomCode, roomCodes,
                                                 maxClientCount)
                break
            
            match prefix:
                case 0:
                    # Received operation message
                    print('Received operation message.')
                    print(f'msgContent:{msgContent}\n')
                case 1:
                    # Received normal message
                    msgContent = rstrip_message(msgContent.decode())
                    handle_client_normal_message(client, msgContent, clients, 
                                                 rooms, roomCode)
                case 2:
                    # Received file-upload request
                    print(f'client [{address}] is uploading a file.\n')
                    
                    # Receive metadata from client
                    msg = client.recv(chunkSize)
                    prefix, metadataBytes = get_prefix_and_content(msg)
                    
                    # Receive file chunks from client
                    recv_file_from_client(client, metadataBytes, chunkSize)
                case 3:
                    # Received file-download request
                    print(f'client [{address}] is downloading a file.\n')
                    
                    clientFilepath, filename = get_filepath_and_filename(msgContent)
                    print(f'clientFilepath: [{clientFilepath}]')
                    
                    # Inform the client to get ready to receive server response
                    send_msg_with_prefix(client, clientFilepath, 2)

                    # Try finding the requested file on server
                    filepath = find_file_in_directory(filename, 'test_files')
                    
                    if filepath == None:
                        # Filename found in test_files folder
                        send_msg_with_prefix(client, 'file_not_found', 0)
                    else:
                        # Filename does not exist in test_files folder
                        send_msg_with_prefix(client, 'file_exists', 0)
                        # Send file to client
                        send_file_to_client(client, filepath, chunkSize)
                case _: 
                    # Received invalid prefix
                    print(f'Received invalid prefix: {typePrefix}.')
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            print(f'Error: [{e}]. ',
                  f'Removed [{address}] from client socket list.')
            handle_client_disconnect_request(client, clients, address, 
                                             rooms, roomCode, roomCodes,
                                             maxClientCount)            
            break
    return
