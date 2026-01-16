# handle_client.py

from general.message import get_prefix_and_content
from server_only.handle_requests.handle_request import handle_request
from server_only.server_core.remove_client import handle_disconnect_request

def handle_one_client(shutdown_event, client_obj, clients, chunk_size, room,
                      rooms, room_codes, max_client_count, max_file_size, ext_list,
                      using_open_ai):
    client = client_obj.get_socket()
    username = client_obj.get_username()
    address = client_obj.get_address()
    room_code = client_obj.get_room_code()
    
    while not shutdown_event.is_set():
        try:
            msg = client.recv(chunk_size) # 1025 bytes
            type_prefix, msg_content = get_prefix_and_content(msg)
            prefix = int.from_bytes(type_prefix, byteorder='big')
            
            print(f'msg: [{msg}]')
            print(f'Type Prefix: [{type_prefix}]')
            print(f'Content: [{msg_content}]')
            print(f'Prefix: [{prefix}]')

            # Empty message -> client closed connection
            if not msg:
                handle_disconnect_request(client, address, clients, 
                                          rooms, room_code, room_codes,
                                          max_client_count)
                break
            
            handle_request(prefix, client, username, msg_content, clients, 
                           room, room_code, address, chunk_size, max_file_size, 
                           ext_list, type_prefix, using_open_ai)
        except (BrokenPipeError, 
                ConnectionResetError, 
                ConnectionAbortedError) as e:
            # Close connection with this client
            print(f'Error: [{e}]. ',
                  f'Removed [{address}] from client socket list.')
            handle_disconnect_request(client, address, clients, 
                                      rooms, room_code, room_codes,
                                      max_client_count)            
            break
    return
