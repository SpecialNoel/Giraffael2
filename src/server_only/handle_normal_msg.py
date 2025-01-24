# handle_normal_msg.py

from datetime import datetime
from general.message import rstrip_message, send_msg_with_prefix
from server_only.check_client_alive import check_client_alive
from server_only.remove_client import remove_client_from_clients

def handle_normal_msg(client, msgContent, clients, rooms, roomCode):
    msg = rstrip_message(msgContent.decode())

    # A list used to remove disconnected client sockets
    clientSocketsToBeRemoved = []
    
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    
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
        
    # Remove disconnected clients
    for socket in clientSocketsToBeRemoved:
        remove_client_from_clients(socket, clients)
        socket.close()
    return
