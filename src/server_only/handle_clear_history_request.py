# handle_clear_history_request.py

from general.message import send_msg_with_prefix

def handle_clear_history_request(client, address, msgContent, room):
    historyToClear = msgContent.decode().lower()
    
    match historyToClear:
        case 'msg':
            room.clearMsgHistory()
            msg = f'Cleared msg history of room [{room.get_room_code()}].'
            send_msg_with_prefix(client, msg, 5)
            print(msg + '\n')
        case 'file':
            room.clearFileHistory()
            msg = f'Deleted files stored in room [{room.get_room_code()}].'
            send_msg_with_prefix(client, msg, 5)
            print(msg + '\n')
        case 'all':
            room.clearMsgHistory()
            room.clearFileHistory()
            msg = (f'Cleared msg history, and deleted files stored in room'
                  +f'[{room.get_room_code()}].')
            send_msg_with_prefix(client, msg, 5)
            print(msg + '\n')
        case _:
            send_msg_with_prefix(client, 'INVALID', 5)
            print(f'Received invalid clear history request from',
                  f'Client [{address}].')

    