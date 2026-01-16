# handle_display_history_request.py

import pickle
from general.message import add_prefix

def handle_display_history_request(client, address, msg_content, room):
    history_to_display = msg_content.decode().lower()
    
    if history_to_display == 'msg':
        msg_list = room.get_message_list()
        client.send(add_prefix(pickle.dumps(msg_list), 4))
        print(f'Sent msg history of room [{room.get_room_code()}] to',
                f'Client [{address}].\n')
    elif history_to_display == 'file':
        file_list = room.get_stored_files()
        client.send(add_prefix(pickle.dumps(file_list), 4))
        print(f'Sent file history of room [{room.get_room_code()}] to',
                f'Client [{address}].\n')
    else:
        client.send(add_prefix(pickle.dumps('INVALID'), 4))
        print(f'Received invalid display history request from',
                f'Client [{address}].\n')
    return
    