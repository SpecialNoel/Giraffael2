# client_onboarding.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[2] # grandparent level
sys.path.append(str(src_folder))
from server_only.mongodb_related.room_ops.list_op import get_roomCodes

from general.message import recv_decoded_content, send_msg_with_prefix
    
def recv_response_on_creating_room(client, chunkSize):
    # Obtain response from client about create or enter room
    # 'C' for create room; 'E' for enter room
    response = recv_decoded_content(client, chunkSize).upper()
    
    # Repeat until response from client is either 'C' or 'E'
    while response != 'C':
        # Client chooses to enter an existing room
        if response == 'E': 
            return False
        
        # Prompt the client to send their response again
        print(f'Error: Client response on creating room: [{response}].')
        msgToClient = ('Error: Response should only be <C> or <E>. ' +
                       'Please try again.')
        send_msg_with_prefix(client, msgToClient, 0)
        response = recv_decoded_content(client, chunkSize).upper()
    # Client chooses to create a new room
    return True
    
def handle_room_code_message(client, chunkSize):
    def check_room_code_validness(roomCode, roomCodes):
        # Check if the received room code already exists in roomCodes
        return roomCode in roomCodes
    
    roomCodes = get_roomCodes()

    # Obtain room code from client
    msg = 'Please enter the room code, OR type <C> to create room.'
    send_msg_with_prefix(client, msg, 0)
    roomCode = recv_decoded_content(client, chunkSize)

    # Repeat until room code sent by client is valid
    while not check_room_code_validness(roomCode, roomCodes):
        # Client choose to create a new room instead
        if roomCode.upper() == 'C':
            return True, ''
        
        # Prompt the client to send their response again
        print(f'Error: Room code: [{roomCode}] does not exist.')
        msg = 'Error: Room code not found. Please try again.'
        send_msg_with_prefix(client, msg, 0)
        roomCode = recv_decoded_content(client, chunkSize)

    # Client successfully entered a valid room code. Acknowledge it to the client
    send_msg_with_prefix(client, 'VALID_ROOM_CODE', 0)
    return False, roomCode

def handle_username_message(client, charPools, chunkSize, maxUsernameLength):
    def check_username_validness(username, charPools, maxUsernameLength):
        # Check if the length of the username is in bound
        if len(username) <= 0 or len(username) > maxUsernameLength:
            return False 
        
        # Check if every character in username is either a letter or a digit
        for char in username:
            if char not in charPools: 
                return False
        return True
    
    # Obtain username from client
    username = recv_decoded_content(client, chunkSize)
    
    # Repeat until username sent by client is valid
    while not check_username_validness(username, charPools, maxUsernameLength):
        # Prompt the client to send their response again
        print(f'Error: Username [{username}] is invalid.')
        msgToClient = ('Error: Username is invalid. Please try again.\n'
                    + f'Username max length: [{maxUsernameLength}]\n'
                     + 'Username can be a combination of lower, upper '
                     + 'cased letters and/or digits.\n')
        send_msg_with_prefix(client, msgToClient, 0)
        username = recv_decoded_content(client, chunkSize)

    # Acknowledge client about username being valid
    send_msg_with_prefix(client, 'VALID_USERNAME', 0)
    return username
