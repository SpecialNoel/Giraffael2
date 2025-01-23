# accept_connection.py

from general.client_obj import Client_Obj
from general.message import send_msg_with_prefix
from server_only.handle_client import handle_one_client
from server_only.recv_from_client import (get_client_response_on_creating_room,
                                          handle_client_room_code_message,
                                          handle_client_username_message)
from server_only.room_code_operations import generate_and_send_room_code
from server_only.room_operations import (create_room, enter_room, 
                                         print_info_when_client_enter_room)
                                          
def test_reach_max_client_count(conn, address, clients, maxClientCount):
    # Disconnect from the connection if reached max client count already
    if len(clients) >= maxClientCount:
        print(f'Max client count [{maxClientCount}] reached.',
              f'Refused connection from [{address}].\n')
        send_msg_with_prefix(conn, '-1', 0)
        conn.close()
        return True
    
    # Otherwise, acknowledge client with 'len(clients)+1'
    send_msg_with_prefix(conn, str((len(clients)+1)), 0)
    return False

def accept_a_connection(conn, address, clients, rooms, roomCodes,
                        charPools, shutdownEvent, chunkSize, roomCodeLength,
                        maxUsernameLength, maxClientCount):
    # If reached max client count before this client: 
    #   disconnect, then acknowledge the client about the disconnection
    # Otherwise, acknowledge the client about the successful connection
    if test_reach_max_client_count(conn, address, clients, maxClientCount):
        return True
    
    # Wait for client to either create or enter room
    wantCreateRoom = get_client_response_on_creating_room(conn, chunkSize)
    
    if wantCreateRoom:
        # Client chooses to create a new room
        roomCode = generate_and_send_room_code(conn, address, charPools, 
                                               roomCodes, roomCodeLength)
    else:
        # Client chooses to enter an existing room
        # Wait for client to send valid room code
        createInstead, roomCode = handle_client_room_code_message(
                                                conn, address, roomCodes,
                                                chunkSize, charPools, 
                                                roomCodeLength)
        if createInstead: 
            wantCreateRoom = True

    # Wait for client to send valid username
    username = handle_client_username_message(conn, charPools, chunkSize,
                                              maxUsernameLength)
    
    # Create a client obj for this client
    clientObj = Client_Obj(conn, address, username, roomCode)
    clients.append(clientObj)
    
    # Create the room if the client has chosen to do so
    if wantCreateRoom:
        create_room(roomCode, rooms)

    # Make the client enter the room
    enter_room(clientObj, roomCode, rooms)
    print_info_when_client_enter_room(address, username, clients, roomCode,
                                      rooms, maxClientCount)

    # Start handling this client
    handle_one_client(shutdownEvent, clientObj, clients, chunkSize,
                      rooms, roomCodes, maxClientCount)
    return
