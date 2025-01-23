# recv_from_client.py

import json
from datetime import datetime
from general.file_transmission import (check_metadata_format,
                                      recv_file, split_metadata)
from general.message import (recv_decoded_content, 
                             send_msg_with_prefix)
from server_only.check_client_alive import check_client_alive
from server_only.remove_client import remove_client_from_clients
from server_only.room_code_operations import generate_and_send_room_code

def check_room_code_validness(roomCode, roomCodes):
    # Check if the received room code exists in roomCodes
    return roomCode in roomCodes

def check_username_validness(username, charPools, maxUsernameLength):
    # Check if the length of the username is in bound
    if len(username) <= 0 or len(username) > maxUsernameLength:
        return False 
    
    # Check if every character in username is either a letter or a digit
    for char in username:
        if char not in charPools: 
            return False
    return True
    
def get_client_response_on_creating_room(client, chunkSize):
    # Obtain response from client about create or enter room
    # 'C' for create room
    # 'E' for enter room
    response = recv_decoded_content(client, chunkSize).upper()
    
    # Repeat until response from client is either 'C' or 'E'
    while response != 'C':
        # Client chooses to enter room
        if response == 'E': 
            return False
        
        msgToClient = ('Error: Response should only be <C> or <E>. ' +
                       'Please try again.')
        send_msg_with_prefix(client, msgToClient, 0)
        
        print(f'Error: Client response on creating room: [{response}].')
        response = recv_decoded_content(client, chunkSize).upper()
    # Client chooses to create room
    return True
    
def handle_client_room_code_message(client, address, roomCodes, 
                                    chunkSize, charPools, 
                                    roomCodeLength):
    createRoomInstead = False

    # Obtain room code from client
    msg = 'Please enter the room code, OR type <C> to create room.'
    send_msg_with_prefix(client, msg, 0)
    roomCode = recv_decoded_content(client, chunkSize).upper()

    # Repeat until room code sent by client is valid
    # OR, client chooses to create a room instead
    while not check_room_code_validness(roomCode, roomCodes):
        if roomCode.upper() == 'C':
            createRoomInstead = True
            return (createRoomInstead, 
                    generate_and_send_room_code(client, address, 
                                                charPools, roomCodes, 
                                                roomCodeLength))
        
        print(f'Error: Room code: [{roomCode}] does not exist.')
        msg = 'Error: Room code not found. Please try again.'
        send_msg_with_prefix(client, msg, 0)
        roomCode = recv_decoded_content(client, chunkSize).upper()

    # Need to acknowledge client about valid room code here
    send_msg_with_prefix(client, 'VALID_ROOM_CODE', 0)
    return createRoomInstead, roomCode

def handle_client_username_message(client, charPools, chunkSize, 
                                   maxUsernameLength):
    # Obtain username from client
    username = recv_decoded_content(client, chunkSize)
    
    # Repeat until username sent by client is valid
    while not check_username_validness(username, charPools, maxUsernameLength):
        msgToClient = 'Error: Username is invalid. Please try again.\n'
        msgToClient += f'Username max length: [{maxUsernameLength}]\n'
        msgToClient += 'Username can be a combination of lower, upper '
        msgToClient += 'cased letters and/or digits.\n'
        send_msg_with_prefix(client, msgToClient, 0)
        
        print(f'Error: Username [{username}] is invalid.')
        username = recv_decoded_content(client, chunkSize)

    # Acknowledge client about username being valid
    send_msg_with_prefix(client, 'VALID_USERNAME', 0)
    return username

def handle_client_normal_message(client, msg, clients, rooms, roomCode):        
    # A list used to remove disconnected client sockets
    clientSocketsToBeRemoved = []
    
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    
    # Broadcast received message to all clients within the same room
    for clientObject in room.get_client_list():
        socket = clientObject.get_socket()
        # If the client has disconnected, remove it
        if not check_client_alive(socket):
            clientSocketsToBeRemoved.append(socket)
            continue
        
        # Otherwise, send received message to this client
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msgWithTime = f'[{date_now} {client.getpeername()}: {msg}]'
        print(msgWithTime+'\n')
        send_msg_with_prefix(socket, msgWithTime, 1)
        
    # Remove disconnected clients
    for socket in clientSocketsToBeRemoved:
        remove_client_from_clients(socket, clients)
        socket.close()
    return

def recv_file_from_client(client, metadataBytes, chunkSize):
    # Obtain metadata
    metadata_json = metadataBytes.decode('utf-8')
    metadata = json.loads(metadata_json)
    print(f'Metadata: [{metadata}].')
    if not check_metadata_format(metadata):
        return
    
    # Split the metadata of the file received from client
    filename, filesize = split_metadata(metadataBytes)
    filepath = 'received_files'

    # Receive the whole file from client
    recv_file(filename, filepath, filesize, client, 
             chunkSize, client.getpeername())
    return
