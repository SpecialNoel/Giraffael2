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
                        maxUsernameLength, maxClientCount, maxFileSize, 
                        extList, usingOpenAI):
    # If reached max client count before this client: 
    #   disconnect, then acknowledge the client about the disconnection
    # Otherwise, acknowledge the client about the successful connection
    if test_reach_max_client_count(conn, address, clients, maxClientCount):
        return
    
    # Wait for client to either create or enter room
    wantCreateRoom = recv_response_on_creating_room(conn, chunkSize)
    
    if wantCreateRoom:
        # Client chooses to create a new room
        roomCode = generate_and_send_room_code(conn, address, charPools, 
                                               roomCodes, roomCodeLength)
    else:
        # Client chooses to enter an existing room
        # Wait for client to send valid room code
        createInstead, roomCode = handle_room_code_message(
                                                conn, address, roomCodes,
                                                chunkSize, charPools, 
                                                roomCodeLength)
        if createInstead: 
            wantCreateRoom = True

    # Wait for client to send valid username
    username = handle_username_message(conn, charPools, chunkSize,
                                              maxUsernameLength)
    
    # Create the room if the client has chosen to do so
    if wantCreateRoom:
        room = create_room_locally(roomCode, rooms)
        create_room(roomCode) # Create a room with roomCode in database
        
    # Create a client obj for this client
    clientObj = Client_Obj(conn, address, username, roomCode)
    add_client_to_list(clientObj, roomCode) # Add the clientObj to the room with roomCode in database
    
    clients.append(clientObj)

    # Make the client enter the room
    room = enter_room(clientObj, roomCode, rooms)
    print_info_when_client_enter_room(address, username, clients, roomCode,
                                      rooms, maxClientCount)

    # Start handling this client
    handle_one_client(shutdownEvent, clientObj, clients, chunkSize, room,
                      rooms, roomCodes, maxClientCount, maxFileSize, extList,
                      usingOpenAI)
    return
