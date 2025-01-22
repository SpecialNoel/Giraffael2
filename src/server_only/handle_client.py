# handle_client.py

from general.file_transmission import find_file_in_directory
from general.message import add_prefix, get_prefix_and_content, rstrip_message
from server_only.remove_client import handle_client_disconnect_request
from server_only.recv_from_client import (handle_client_normal_message,
                                          recv_file_from_client)
from server_only.send_to_client import send_file_to_client

def handle_one_client(shutdownEvent, clientObj, clients, chunkSize,
                      rooms, roomCodes, maxClientCount, msgContentSize):
    client = clientObj.get_socket()
    address = clientObj.get_address()
    roomCode = clientObj.get_room_code()
    
    while not shutdownEvent.is_set():
        try:
            msg = client.recv(chunkSize) # 1025 bytes
            typePrefix, msgContent = get_prefix_and_content(msg)
            print(f'msg: [{msg}]')
            print(f'Type Prefix: [{typePrefix}]')
            print(f'Content: [{msgContent}]')
            prefix = int.from_bytes(typePrefix, byteorder='big')
            print(f'Prefix: [{prefix}]')

            # Empty message -> client closed connection
            if not msg:
                handle_client_disconnect_request(client, clients, address, 
                                                rooms, roomCode, roomCodes,
                                                maxClientCount)
                break
            
            match prefix:
                case 0:
                    # Received normal message
                    msgContent = rstrip_message(msgContent.decode())
                    handle_client_normal_message(client, msgContent, clients, 
                                                 rooms, roomCode)
                case 1:
                    # Received file-upload request
                    print(f'client [{address}] is uploading a file.\n')
                    
                    # Receive metadata from client
                    msg = client.recv(chunkSize)
                    typePrefix, msgContent = get_prefix_and_content(msg)
                    # Receive file chunks from client
                    recv_file_from_client(client, msgContent, msgContentSize)
                case 2:
                    # Received file-download request
                    print(f'client [{address}] is downloading a file.\n')
                    
                    # msgContent is the filepath client wants to store
                    #   the file on their machine
                    clientFilepath = rstrip_message(msgContent.decode())
                    print(f'clientFilepath: [{clientFilepath}]')
                    
                    # Inform the client to get ready to receive server response
                    client.send(add_prefix(clientFilepath.encode(), 1))
                    
                    # Receive filename from client
                    msg = client.recv(chunkSize) # 1025 bytes
                    typePrefix, msgContent = get_prefix_and_content(msg)
                    filename = rstrip_message(msgContent.decode())
                    filepath = find_file_in_directory(filename, 'test_files')
                    
                    if filepath == None:
                        # Filename found in test_files folder
                        client.send(b'file_not_found')
                    else:
                        # Filename does not exist in test_files folder
                        client.send(b'file_exists')
                        # Send file to client
                        send_file_to_client(client, filepath, msgContentSize)
                case _: 
                    # Received invalid prefix
                    print(f'Received invalid prefix: {typePrefix}.')
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            print(f'Error: [{e}]. ',
                  f'Removed [{address}] from client socket list.')
            handle_client_disconnect_request(client, address, roomCode)
            break
    return
