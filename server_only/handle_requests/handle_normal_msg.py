# handle_normal_msg.py

from datetime import datetime
from general.message import rstrip_message, send_msg_with_prefix
from server_only.server_core.check_client_alive import check_client_alive
from server_only.server_core.remove_client import remove_client_from_clients
from server_only.mongodb_related.msg_ops.add_op import add_msg_to_history
from server_only.mongodb_related.client_ops.delete_op import delete_client_to_list

def handle_normal_msg(client, address, username, msg_content, clients, room):
    msg = rstrip_message(msg_content.decode())

    # A list used to remove disconnected client sockets
    client_sockets_to_be_removed = []
    msg_added_to_msg_list = False
        
    # Broadcast received message to all clients within the same room
    for client_object in room.get_client_list():
        socket = client_object.get_socket()
        # If the client has disconnected, remove it
        if not check_client_alive(socket):
            client_sockets_to_be_removed.append(socket)
            continue
        
        # Otherwise, send received message to this client
        date_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        msg_with_time = f'[{date_now} <{username}>: {msg}]'
        print(msg_with_time+'\n')
        send_msg_with_prefix(socket, msg_with_time, 1)
        
        # Update '__message_list' in room
        if not msg_added_to_msg_list:
            msg_added_to_msg_list = True
            room.add_message_to_message_list(msg_with_time)
            add_msg_to_history(room.get_room_code(), 
                               'sender_id',
                               username,
                               msg_with_time)
            msg_with_time = f'[{date_now} <{username}>{address}: {msg}]'
            room.add_message_to_message_list_for_server(msg_with_time)
            print(f'Current messages in Room [{room.get_room_code()}]:',
                  f'{room.get_message_list_for_server()}.')
        
    # Remove disconnected clients
    for socket in client_sockets_to_be_removed:
        remove_client_from_clients(socket, clients)
        delete_client_to_list(address, room.get_room_code())
        socket.close()
    return
