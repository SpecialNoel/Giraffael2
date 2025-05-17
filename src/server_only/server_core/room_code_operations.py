# room_code_operations.py

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[2] # grandparent level
sys.path.append(str(src_folder))
from server_only.mongodb_related.room_ops.list_op import get_roomCodes

import secrets
from general.message import send_msg_with_prefix


def generate_room_code(charPools, roomCodeLength):
    # Generate an unique room code with roomCodeLength characters
    # Each character is either a letter (upper or lower) or a digit
    roomCodes = get_roomCodes()
    
    roomCode = ''.join(secrets.choice(charPools) for _ in range(roomCodeLength))
    while roomCode in roomCodes:
        roomCode = ''.join(secrets.choice(charPools) for _ in range(roomCodeLength))
    return roomCode

def send_room_code(conn, address, roomCode):
    # Send the generated room code to the client
    send_msg_with_prefix(conn, roomCode, 0)
    print(f'Sent room code [{roomCode}] to client [{address}].')
    return 
