# handle_normal_msg.py

from datetime import datetime
from general.message import rstrip_message, send_msg_with_prefix
from server_only.server_core.check_client_alive import check_client_alive
from server_only.server_core.remove_client import remove_client_from_clients
from server_only.mongodb_related.msg_ops.add_op import add_msg_to_history
from server_only.mongodb_related.client_ops.delete_op import delete_client_to_list

def handle_normal_msg(client, address, username, msgContent, clients, room):
    msg = rstrip_message(msgContent.decode())

    # A list used to remove disconnected client sockets
    clientSocketsToBeRemoved = []
    
    msgAddedToMsgList = False
        
    # Broadcast received message to all clients within the same room
    for clientObject in room.get_client_list():
        socket = clientObject.get_socket()
        # If the client has disconnected, remove it
        if not check_client_alive(socket):
            clientSocketsToBeRemoved.append(socket)
            continue
        
        # Otherwise, send received message to this client
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msgWithTime = f'[{date_now} <{username}>: {msg}]'
        print(msgWithTime+'\n')
        send_msg_with_prefix(socket, msgWithTime, 1)
        
        # Update '__messageList' in room
        if not msgAddedToMsgList:
            msgAddedToMsgList = True
            room.add_message_to_message_list(msgWithTime)
            add_msg_to_history(room.get_room_code(), 
                               'senderID',
                               username,
                               msgWithTime)
            msgWithTime = f'[{date_now} <{username}>{address}: {msg}]'
            room.add_message_to_message_list_for_server(msgWithTime)
            print(f'Current messages in Room [{room.get_room_code()}]:',
                  f'{room.get_message_list_for_server()}.')
        
    # Remove disconnected clients
    for socket in clientSocketsToBeRemoved:
        remove_client_from_clients(socket, clients)
        delete_client_to_list(address, room.get_room_code())
        socket.close()
    return
