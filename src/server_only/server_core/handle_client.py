# handle_client.py

from general.message import get_prefix_and_content
from server_only.server_core.handle_request import handle_request
from server_only.server_core.remove_client import handle_disconnect_request

def handle_one_client(shutdownEvent, clientObj, chunkSize, 
                      roomCode, maxFileSize, extList, usingOpenAI):
    client = clientObj.get_socket()
    username = clientObj.get_username()
    address = clientObj.get_address()
    
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
                handle_disconnect_request(client, address, roomCode)
                break
            
            handle_request(prefix, client, username, msgContent, 
                           roomCode, address, chunkSize, maxFileSize, 
                           extList, typePrefix, usingOpenAI)
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            print(f'Error: [{e}]. ',
                  f'Removed [{address}] from client socket list.')
            handle_disconnect_request(client, address, roomCode)
          
            break
    return
