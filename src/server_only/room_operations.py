# room_operations.py

from general.room import Room

def create_room(roomCode, rooms):
    room = Room(roomCode)
    rooms.append(room)
    print(f'Created room with room code [{roomCode}]') 
    return

def enter_room(clientObj, roomCode, rooms):
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    room.add_client_to_client_list(clientObj)
    address = clientObj.get_address()
    print(f'Client [{address}] entered room [{roomCode}].\n')
    return
    
def print_room_status(room):
    print(f'Connected clients in room [{room.get_room_code()}]:',
          f'{len(room.get_client_list())}')
    for idx, clientObj in enumerate(room.get_client_list()):
        print(f'Client {idx+1}: [{clientObj.get_username()},',
              f'{clientObj.get_address()}]')
    print('')
    return

def print_info_when_client_enter_room(address, username, clients, 
                                      roomCode, rooms, maxClientCount):
    print(f'Accepted connection request from Client on [{address}].')
    print(f'With Username: [{username}], room code: [{roomCode}].')
    print('All connected clients: ',
         f'[{len(clients)}/{maxClientCount}]')
    room = [r for r in rooms if r.get_room_code() == roomCode][0]
    print_room_status(room)
    return
