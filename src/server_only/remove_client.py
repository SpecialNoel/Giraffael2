# remove_client.py

from server_only.room_operations import print_room_status

def remove_client_from_clients(client, clients):
    # Get address of client
    address = client.getpeername()
    
    # Remove client from clients based on address
    for clientObj in clients:
        if clientObj.get_address() == address:
            clients.remove(clientObj)
            break
    return

def remove_client_from_room(client, room):
    # Remove client from the room it was in
    room.remove_client_from_client_list(client)
    return room

def handle_disconnect_request(client, clients, address, rooms, 
                              roomCode, roomCodes, maxClientCount):
    print(f'Client on [{client.getpeername()}] disconnected.')
    
    # Remove client from client list
    remove_client_from_clients(client, clients)
    client.close()
    print(f'All connected clients: ',
          f'[{len(clients)}/{maxClientCount}]')
    
    # Remove client from the room it was in
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    room = remove_client_from_room(address, room)
    print_room_status(room)
    
    # Remove room code from roomCodes if its corresponding room is empty
    if len(room.get_client_list()) == 0:
        roomCodes.remove(roomCode)
        print(f'Room [{roomCode}] is empty, removed from room codes.\n')
        # Remove the file-storing folder for that room as well
        room.delete_file_storing_folder()
    return
