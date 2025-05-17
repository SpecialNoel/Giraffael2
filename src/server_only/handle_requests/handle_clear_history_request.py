# handle_clear_history_request.py

from general.message import send_msg_with_prefix

def handle_clear_history_request(client, address, msgContent, room):
    historyToClear = msgContent.decode().lower()
    
    if historyToClear == 'msg':
        room.clearMsgHistory()
        msg = f'Cleared msg history of room [{room.get_room_code()}].'
        send_msg_with_prefix(client, msg, 5)
        print(msg + '\n')
    elif historyToClear == 'file':
        room.clearFileHistory()
        msg = f'Deleted files stored in room [{room.get_room_code()}].'
        send_msg_with_prefix(client, msg, 5)
        print(msg + '\n')
    elif historyToClear == 'all':
        room.clearMsgHistory()
        room.clearFileHistory()
        msg = (f'Cleared msg history, and deleted files stored in room'
            +f'[{room.get_room_code()}].')
        send_msg_with_prefix(client, msg, 5)
        print(msg + '\n')
    else:
        send_msg_with_prefix(client, 'INVALID', 5)
        print(f'Received invalid clear history request from',
            f'Client [{address}].')
    return
    