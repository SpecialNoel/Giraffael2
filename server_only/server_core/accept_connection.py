# accept_connection.py

from server_only.mongodb_related.client_ops.add_op import add_client_to_list
from server_only.mongodb_related.room_ops.create_op import create_room

from general.client_obj import Client_Obj
from general.message import send_msg_with_prefix
from server_only.server_core.handle_client import handle_one_client
from server_only.server_core.client_onboarding import (recv_response_on_creating_room,
                                          handle_room_code_message,
                                          handle_username_message)
from server_only.server_core.room_code_operations import generate_and_send_room_code
from server_only.server_core.room_operations import (create_room_locally, enter_room, 
                                         print_info_when_client_enter_room)
                                          
def test_reach_max_client_count(conn, address, clients, max_client_count):
    # Disconnect from the connection if reached max client count already
    if len(clients) >= max_client_count:
        print(f'Max client count [{max_client_count}] reached.',
              f'Refused connection from [{address}].\n')
        send_msg_with_prefix(conn, '-1', 0)
        conn.close()
        return True
    
    # Otherwise, acknowledge client with 'len(clients)+1'
    send_msg_with_prefix(conn, str((len(clients)+1)), 0)
    return False

def accept_a_connection(conn, address, clients, rooms, room_codes,
                        char_pools, shutdown_event, chunk_size, room_code_length,
                        max_username_length, max_client_count, max_file_size, 
                        ext_list, using_open_ai):
    # If reached max client count before this client: 
    #   disconnect, then acknowledge the client about the disconnection
    # Otherwise, acknowledge the client about the successful connection
    if test_reach_max_client_count(conn, address, clients, max_client_count):
        return
    
    # Wait for client to either create or enter room
    want_to_create_room = recv_response_on_creating_room(conn, chunk_size)
    
    if want_to_create_room:
        # Client chooses to create a new room
        room_code = generate_and_send_room_code(conn, address, char_pools, 
                                               room_codes, room_code_length)
    else:
        # Client chooses to enter an existing room
        # Wait for client to send valid room code
        want_to_create_instead, room_code = handle_room_code_message(
                                                conn, address, room_codes,
                                                chunk_size, char_pools, 
                                                room_code_length)
        if want_to_create_instead: 
            want_to_create_room = True

    # Wait for client to send valid username
    username = handle_username_message(conn, char_pools, chunk_size,
                                              max_username_length)
    
    # Create the room if the client has chosen to do so
    if want_to_create_room:
        room = create_room_locally(room_code, rooms)
        create_room(room_code) # Create a room with room_code in database
        
    # Create a client obj for this client
    client_obj = Client_Obj(conn, address, username, room_code)
    add_client_to_list(client_obj, room_code) # Add the client_obj to the room with room_code in database
    
    clients.append(client_obj)

    # Make the client enter the room
    room = enter_room(client_obj, room_code, rooms)
    print_info_when_client_enter_room(address, username, clients, room_code,
                                      rooms, max_client_count)

    # Start handling this client
    handle_one_client(shutdown_event, client_obj, clients, chunk_size, room,
                      rooms, room_codes, max_client_count, max_file_size, ext_list,
                      using_open_ai)
    return
