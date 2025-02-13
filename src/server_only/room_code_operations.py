# room_code_operations.py

import secrets
from general.message import send_msg_with_prefix

def generate_room_code(charPools, roomCodes, roomCodeLength):
    # Generate an unique room code with roomCodeLength characters
    # Each character is either a letter (upper or lower) or a digit
    roomCode = ''.join(secrets.choice(charPools) 
                for _ in range(roomCodeLength))
    while roomCode in roomCodes:
        roomCode = ''.join(secrets.choice(charPools) 
                    for _ in range(roomCodeLength))
    roomCodes.add(roomCode)
    return roomCode

def generate_and_send_room_code(conn, address, charPools, roomCodes, 
                                roomCodeLength):
    # Generate an unique room code for this client
    roomCode = generate_room_code(charPools, roomCodes, roomCodeLength)
    # Send the generated room code to the client
    send_msg_with_prefix(conn, roomCode, 0)
    print(f'Sent room code [{roomCode}] to client [{address}].')
    return roomCode
