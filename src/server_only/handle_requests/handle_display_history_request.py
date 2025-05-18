# handle_display_history_request.py

import pickle
from general.message import add_prefix

import sys
from pathlib import Path
src_folder = Path(__file__).resolve().parents[2] # grandparent level
sys.path.append(str(src_folder))
from server_only.mongodb_related.msg_ops.list_op import get_msg_history
from server_only.mongodb_related.file_ops.list_op import get_file_history

def handle_display_history_request(clientObj, msgContent, room):
    address = clientObj.get_address()
    client = clientObj.get_socket()
    roomCode = room.get_room_code()
    
    historyToDisplay = msgContent.decode().lower()
    
    if historyToDisplay == 'msg':
        msgList = get_msg_history(roomCode)
        client.send(add_prefix(pickle.dumps(msgList), 4))
        print(f'Sent msg history of room [{room.get_room_code()}] to [{address}].\n')
    elif historyToDisplay == 'file':
        fileList = get_file_history(roomCode)
        client.send(add_prefix(pickle.dumps(fileList), 4))
        print(f'Sent file history of room [{room.get_room_code()}] to [{address}].\n')
    else:
        client.send(add_prefix(pickle.dumps('INVALID'), 4))
        print(f'Received invalid display history request from [{address}].\n')
    return
    