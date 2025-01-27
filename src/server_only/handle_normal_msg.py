# handle_normal_msg.py

from datetime import datetime
from general.message import rstrip_message, send_msg_with_prefix
from server_only.check_client_alive import check_client_alive
from server_only.remove_client import remove_client_from_clients

def handle_normal_msg(client, msgContent, clients, rooms, room, roomCode):
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
        msgWithTime = f'[{date_now} {client.getpeername()}: {msg}]'
        print(msgWithTime+'\n')
        send_msg_with_prefix(socket, msgWithTime, 1)
        
        # Update '__messageList' in room
        if not msgAddedToMsgList:
            msgAddedToMsgList = True
            room.add_message_to_message_list(msgWithTime)
            print(f'Current messages in Room [{room.get_room_code()}]:',
                  f'{room.get_message_list()}.')
        
    # Remove disconnected clients
    for socket in clientSocketsToBeRemoved:
        remove_client_from_clients(socket, clients)
        socket.close()
    return
