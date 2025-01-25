# recv_from_client.py

from general.message import (recv_decoded_content, 
                             send_msg_with_prefix)
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
    
def recv_response_on_creating_room(client, chunkSize):
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
    
def handle_room_code_message(client, address, roomCodes, 
                                    chunkSize, charPools, 
                                    roomCodeLength):
    createRoomInstead = False

    # Obtain room code from client
    msg = 'Please enter the room code, OR type <C> to create room.'
    send_msg_with_prefix(client, msg, 0)
    roomCode = recv_decoded_content(client, chunkSize)

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
        roomCode = recv_decoded_content(client, chunkSize)

    # Need to acknowledge client about valid room code here
    send_msg_with_prefix(client, 'VALID_ROOM_CODE', 0)
    return createRoomInstead, roomCode

def handle_username_message(client, charPools, chunkSize, 
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
