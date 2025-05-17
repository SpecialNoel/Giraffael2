# remove_client.py

from server_only.mongodb_related.client_ops.delete_op import delete_client_from_list
from server_only.mongodb_related.client_ops.list_op import get_number_of_clients_from_one_room
from server_only.mongodb_related.room_ops.delete_op import delete_room

def handle_disconnect_request(client, address, roomCode):
    client.close()
    print(f'Client on [{address}] disconnected.')
    
    # Remove client from database
    delete_client_from_list(address, roomCode)
    
    # Remove room from database if the room is empty
    if len(get_number_of_clients_from_one_room(roomCode)) == 0:
        delete_room(roomCode)
        print(f'Room [{roomCode}] is empty, removed from database.\n')
    return
