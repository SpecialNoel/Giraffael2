# handle_clear_history_request.py

from general.message import send_msg_with_prefix

def handle_clear_history_request(client, address, msg_content, room):
    history_to_clear = msg_content.decode().lower()
    
    if history_to_clear == 'msg':
        room.clear_msg_history()
        msg = f'Cleared msg history of room [{room.get_room_code()}].'
        send_msg_with_prefix(client, msg, 5)
        print(msg + '\n')
    elif history_to_clear == 'file':
        room.clear_file_history()
        msg = f'Deleted files stored in room [{room.get_room_code()}].'
        send_msg_with_prefix(client, msg, 5)
        print(msg + '\n')
    elif history_to_clear == 'all':
        room.clear_msg_history()
        room.clear_file_history()
        msg = (f'Cleared msg history, and deleted files stored in room'
            +f'[{room.get_room_code()}].')
        send_msg_with_prefix(client, msg, 5)
        print(msg + '\n')
    else:
        send_msg_with_prefix(client, 'INVALID', 5)
        print(f'Received invalid clear history request from',
            f'Client [{address}].')
    return
    