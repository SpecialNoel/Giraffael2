# accept_connection.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[2] # grandparent level
sys.path.append(str(src_folder))

from server_only.mongodb_related.client_ops.add_op import add_client_to_list
from server_only.mongodb_related.client_ops.list_op import get_number_of_clients_from_all_rooms
from server_only.mongodb_related.room_ops.create_op import create_room

from general.client_obj import Client_Obj
from general.message import send_msg_with_prefix
from server_only.server_core.handle_client import handle_one_client
from server_only.server_core.client_onboarding import (recv_response_on_creating_room,
                                                       handle_room_code_message,
                                                       handle_username_message)
from server_only.server_core.room_code_operations import generate_room_code, send_room_code
from server_only.server_core.room import Room 

def test_reach_max_client_count(conn, address, maxClientCount):
    # Disconnect from the connection if reached max client count already
    currentNumberOfClients = get_number_of_clients_from_all_rooms()
    print(f'currentNumberOfClients: [{currentNumberOfClients}]')
    
    if currentNumberOfClients >= maxClientCount:
        print(f'Max client count [{maxClientCount}] reached.',
              f'Refused connection from [{address}].\n')
        send_msg_with_prefix(conn, '-1', 0)
        conn.close()
        return True
    
    # Otherwise, acknowledge client with 'len(currentNumberOfClients)+1'
    send_msg_with_prefix(conn, str((currentNumberOfClients+1)), 0)
    return False

def accept_a_connection(conn, address, clients, rooms, charPools, shutdownEvent, chunkSize, 
                        roomCodeLength, maxUsernameLength, maxClientCount, 
                        maxFileSize, extList, usingOpenAI):
    if test_reach_max_client_count(conn, address, maxClientCount):
        return
    
    # Generate a unique roomCode
    roomCode = generate_room_code(charPools, roomCodeLength)
    room = None
    
    # # Wait for client to either create or enter room
    if recv_response_on_creating_room(conn, chunkSize):
        # Client chooses to create a new room
        send_room_code(conn, address, roomCode)
        create_room(roomCode) # Create a room with roomCode in database
        room = Room(roomCode)
        rooms.append(room)
    else:
        # Client chooses to enter an existing room
        # Wait for client to send valid room code
        clientWantsToCreateRoomInstead, roomCode = handle_room_code_message(conn, chunkSize)
        if clientWantsToCreateRoomInstead:
            roomCode = generate_room_code(charPools, roomCodeLength)
            create_room(roomCode) # Create a room with roomCode in database
            room = Room(roomCode)
            rooms.append(room)
        else:
            for tempRoom in rooms:
                if tempRoom.get_room_code() == roomCode:
                    room = tempRoom
                    break

    # Wait for client to send valid username
    username = handle_username_message(conn, charPools, chunkSize, maxUsernameLength)
        
    # Create a clientObj for this client
    clientObj = Client_Obj(conn, address, username, roomCode)
    clients.append(clientObj.get_socket())
    add_client_to_list(clientObj, roomCode) # Add the clientObj to the room in database
    room.add_client_to_client_list(clientObj) # Add clientObj to the local room obj

    # Start handling this client
    handle_one_client(shutdownEvent, clientObj, clients, room, rooms, chunkSize, roomCode,
                      maxFileSize, extList, usingOpenAI)
    return
