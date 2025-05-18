# handle_normal_msg.py

from general.message import rstrip_message, send_msg_with_prefix
from server_only.server_core.check_client_alive import check_client_alive
from server_only.mongodb_related.msg_ops.add_op import add_msg_to_history
from server_only.mongodb_related.client_ops.delete_op import delete_client_from_list

def handle_normal_msg(clientObj, msgContent, room):
    msg = rstrip_message(msgContent.decode())

    # A list used to remove disconnected client sockets
    clientSocketsToBeRemoved = []
    
    # Broadcast received message to all clients within the same room
    for clientObject in room.get_client_list():
        socket = clientObject.get_socket()
        # If the client has disconnected, remove it
        if not check_client_alive(socket):
            clientSocketsToBeRemoved.append(socket)
            continue
        
        # Otherwise, send received message to this client
        msgWithSenderName = f'[{clientObj.get_username()}]: ' + msg 
        send_msg_with_prefix(socket, msgWithSenderName, 1)

    # Update '__messageList' in room in database
    add_msg_to_history(room.get_room_code(), clientObj.get_uuid(), 
                       clientObj.get_username(), msg)

    # Remove disconnected clients
    for socket in clientSocketsToBeRemoved:
        delete_client_from_list(socket.get_address(), room.get_room_code())
        room.remove_client_from_client_list(socket.get_address())
        socket.close()
    return
