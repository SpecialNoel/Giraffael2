# room_code_operations.py

import secrets
from general.message import send_msg_with_prefix

def generate_room_code(char_pools, room_codes, room_code_length):
    # Generate an unique room code with room_code_length characters
    # Each character is either a letter (upper or lower) or a digit
    room_code = ''.join(secrets.choice(char_pools) 
                for _ in range(room_code_length))
    while room_code in room_codes:
        room_code = ''.join(secrets.choice(char_pools) 
                    for _ in range(room_code_length))
    room_codes.add(room_code)
    return room_code

def generate_and_send_room_code(conn, address, char_pools, room_codes, 
                                room_code_length):
    # Generate an unique room code for this client
    room_code = generate_room_code(char_pools, room_codes, room_code_length)
    # Send the generated room code to the client
    send_msg_with_prefix(conn, room_code, 0)
    print(f'Sent room code [{room_code}] to client [{address}].')
    return room_code
