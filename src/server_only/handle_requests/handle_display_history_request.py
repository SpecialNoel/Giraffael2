# handle_display_history_request.py

import pickle
from general.message import add_prefix

def handle_display_history_request(clientObj, msgContent, room):
    address = clientObj.get_address()
    client = clientObj.get_socket()
    
    historyToDisplay = msgContent.decode().lower()
    
    if historyToDisplay == 'msg':
        msgList = room.get_message_list()
        client.send(add_prefix(pickle.dumps(msgList), 4))
        print(f'Sent msg history of room [{room.get_room_code()}] to',
                f'Client [{address}].\n')
    elif historyToDisplay == 'file':
        fileList = room.get_stored_files()
        client.send(add_prefix(pickle.dumps(fileList), 4))
        print(f'Sent file history of room [{room.get_room_code()}] to',
                f'Client [{address}].\n')
    else:
        client.send(add_prefix(pickle.dumps('INVALID'), 4))
        print(f'Received invalid display history request from',
                f'Client [{address}].\n')
    return
    