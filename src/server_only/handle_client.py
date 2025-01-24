# handle_client.py

from general.message import get_prefix_and_content
from server_only.handle_download_request import handle_download_request
from server_only.handle_normal_msg import handle_normal_msg
from server_only.remove_client import handle_disconnect_request
from server_only.handle_upload_request import handle_upload_request

def handle_one_client(shutdownEvent, clientObj, clients, chunkSize,
                      rooms, roomCodes, maxClientCount, maxFileSize):
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
                handle_disconnect_request(client, clients, address, 
                                          rooms, roomCode, roomCodes,
                                          maxClientCount)
                break
            
            match prefix:
                case 0: # Received operation message
                    print('Received operation message.')
                    print(f'msgContent:{msgContent}\n')
                case 1: # Received normal message
                    handle_normal_msg(client, msgContent, clients, 
                                                 rooms, roomCode)
                case 2: # Received file-upload request
                    handle_upload_request(client, address, 
                                          chunkSize, maxFileSize)
                case 3: # Received file-download request
                    handle_download_request(client, address, 
                                           msgContent, chunkSize, maxFileSize)
                case _: # Received invalid prefix
                    print(f'Received invalid prefix: {typePrefix}.')
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            print(f'Error: [{e}]. ',
                  f'Removed [{address}] from client socket list.')
            handle_disconnect_request(client, clients, address, 
                                      rooms, roomCode, roomCodes,
                                      maxClientCount)            
            break
    return
