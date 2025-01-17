# handle_client.py


from general.message import rstrip_message, get_prefix_and_content
from server_only.remove_client import handle_client_disconnect_request
from server_only.recv_from_client import (handle_client_normal_message,
                                          recv_file_from_client)


def handle_one_client(shutdownEvent, clientObj, clients, chunkSize,
                      rooms, roomCodes, maxClientCount, msgContentSize):
    client = clientObj.get_socket()
    address = clientObj.get_address()
    roomCode = clientObj.get_room_code()
    
    while not shutdownEvent.is_set():
        try:
            msg = client.recv(chunkSize) # 1025 bytes
            typePrefix, msgContent = get_prefix_and_content(msg)
            print(f'msg: {msg}')
            print(f'Type Prefix: {typePrefix}')
            print(f'Content: {msgContent}')
            prefix = int.from_bytes(typePrefix, byteorder='big')
            print(f'Prefix: {prefix}')

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
                    # Received file-transmission request
                    print(f'client [{address}] is transferring a file.\n')
                    
                    # Try receiving metadata from client
                    msg = client.recv(chunkSize)
                    typePrefix, msgContent = get_prefix_and_content(msg)
                    recv_file_from_client(client, msgContent, msgContentSize)
                case _: 
                    # Received invalid prefix
                    print(f'Received invalid prefix: {typePrefix}.')
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            print(f'Error: {e}. ',
                    f'Removed [{address}] from client socket list.')
            handle_client_disconnect_request(client, address, roomCode)
            break
    return