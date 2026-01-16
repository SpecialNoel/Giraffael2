# client_onboarding.py

from general.message import (recv_decoded_content, 
                             send_msg_with_prefix)
from server_only.server_core.room_code_operations import generate_and_send_room_code

def check_room_code_validness(room_code, room_codes):
    # Check if the received room code exists in room_codes
    return room_code in room_codes

def check_username_validness(username, char_pools, max_username_length):
    # Check if the length of the username is in bound
    if len(username) <= 0 or len(username) > max_username_length:
        return False 
    
    # Check if every character in username is either a letter or a digit
    for char in username:
        if char not in char_pools: 
            return False
    return True
    
def recv_response_on_creating_room(client, chunk_size):
    # Obtain response from client about create or enter room
    # 'C' for create room
    # 'E' for enter room
    response = recv_decoded_content(client, chunk_size).upper()
    
    # Repeat until response from client is either 'C' or 'E'
    while response != 'C':
        # Client chooses to enter room
        if response == 'E': 
            return False
        
        msg_to_client = ('Error: Response should only be <C> or <E>. ' +
                       'Please try again.')
        send_msg_with_prefix(client, msg_to_client, 0)
        
        print(f'Error: Client response on creating room: [{response}].')
        response = recv_decoded_content(client, chunk_size).upper()
    # Client chooses to create room
    return True
    
def handle_room_code_message(client, address, room_codes, 
                                    chunk_size, char_pools, 
                                    room_code_length):
    want_to_create_room_instead = False

    # Obtain room code from client
    msg = 'Please enter the room code, OR type <C> to create room.'
    send_msg_with_prefix(client, msg, 0)
    room_code = recv_decoded_content(client, chunk_size)

    # Repeat until room code sent by client is valid
    # OR, client chooses to create a room instead
    while not check_room_code_validness(room_code, room_codes):
        if room_code.upper() == 'C':
            want_to_create_room_instead = True
            return (want_to_create_room_instead, 
                    generate_and_send_room_code(client, address, 
                                                char_pools, room_codes, 
                                                room_code_length))
        
        print(f'Error: Room code: [{room_code}] does not exist.')
        msg = 'Error: Room code not found. Please try again.'
        send_msg_with_prefix(client, msg, 0)
        room_code = recv_decoded_content(client, chunk_size)

    # Need to acknowledge client about valid room code here
    send_msg_with_prefix(client, 'VALID_ROOM_CODE', 0)
    return want_to_create_room_instead, room_code

def handle_username_message(client, char_pools, chunk_size, 
                                   max_username_length):
    # Obtain username from client
    username = recv_decoded_content(client, chunk_size)
    
    # Repeat until username sent by client is valid
    while not check_username_validness(username, char_pools, max_username_length):
        msg_to_client = 'Error: Username is invalid. Please try again.\n'
        msg_to_client += f'Username max length: [{max_username_length}]\n'
        msg_to_client += 'Username can be a combination of lower, upper '
        msg_to_client += 'cased letters and/or digits.\n'
        send_msg_with_prefix(client, msg_to_client, 0)
        
        print(f'Error: Username [{username}] is invalid.')
        username = recv_decoded_content(client, chunk_size)

    # Acknowledge client about username being valid
    send_msg_with_prefix(client, 'VALID_USERNAME', 0)
    return username
