# handle_clear_history_request.py

from general.message import send_msg_with_prefix

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[2] # grandparent level
sys.path.append(str(src_folder))
from server_only.mongodb_related.msg_ops.clear_op import clear_msg_history
from server_only.mongodb_related.file_ops.delete_op import delete_all_files

def handle_clear_history_request(clientObj, msgContent, room):
    address = clientObj.get_address()
    client = clientObj.get_socket()
    roomCode = room.get_room_code()
    
    historyToClear = msgContent.decode().lower()
    
    if historyToClear == 'msg':
        clear_msg_history(roomCode)
        msg = f'Cleared msg history of room [{roomCode}].'
        send_msg_with_prefix(client, msg, 5)
        print(msg + '\n')
    elif historyToClear == 'file':
        delete_all_files(roomCode)
        msg = f'Deleted files stored in room [{roomCode}].'
        send_msg_with_prefix(client, msg, 5)
        print(msg + '\n')
    elif historyToClear == 'all':
        clear_msg_history(roomCode)
        delete_all_files(roomCode)
        msg = (f'Cleared msg history, and deleted files stored in room [{roomCode}].')
        send_msg_with_prefix(client, msg, 5)
        print(msg + '\n')
    else:
        send_msg_with_prefix(client, 'INVALID', 5)
        print(f'Received invalid clear history request from [{address}].')
    return
    