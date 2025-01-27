# handle_request.py

from server_only.handle_clear_history_request import handle_clear_history_request
from server_only.handle_display_history_request import handle_display_history_request
from server_only.handle_download_request import handle_download_request
from server_only.handle_normal_msg import handle_normal_msg
from server_only.handle_upload_request import handle_upload_request

def handle_request(prefix, client, msgContent, clients, 
                   rooms, room, roomCode, address,
                   chunkSize, maxFileSize, extList, typePrefix):
    match prefix:
        case 0:
            # Received operation message
            print('Received operation message.')
            print(f'msgContent:{msgContent}\n')
        case 1: 
            # Received normal message
            handle_normal_msg(client, msgContent, clients, 
                              rooms, room, roomCode)
        case 2: 
            # Received file-upload request
            handle_upload_request(client, address, room, roomCode,
                                  chunkSize, maxFileSize, extList)
        case 3: 
            # Received file-download request
            handle_download_request(client, address, room, roomCode,
                                    msgContent, chunkSize, 
                                    maxFileSize, extList)
        case 4: # Received display msg/file history request
            handle_display_history_request(client, address, msgContent, room)
        case 5: # Received clear msg/file/all history request
            handle_clear_history_request(client, address, msgContent, room)
        case _: # Received invalid prefix
            print(f'Received invalid prefix: {typePrefix}.')
    return
