# handle_client.py

from general.message import get_prefix_and_content
from server_only.handle_request import handle_request
from server_only.remove_client import handle_disconnect_request

def handle_one_client(shutdownEvent, clientObj, clients, chunkSize, room,
                      rooms, roomCodes, maxClientCount, maxFileSize, extList):
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
            
            handle_request(prefix, client, msgContent, clients, 
                           rooms, room, roomCode, address,
                           chunkSize, maxFileSize, extList, typePrefix)
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
