# room_operations.py

from general.room import Room

def create_room_locally(room_code, rooms):
    room = Room(room_code)
    room.create_file_storing_folder()
    rooms.append(room)
    print(f'Created room with room code [{room_code}]') 
    return room

def enter_room(client_obj, room_code, rooms):
    room = [r for r in rooms if r.get_room_code() == room_code][0]
    room.add_client_to_client_list(client_obj)
    address = client_obj.get_address()
    print(f'Client [{address}] entered room [{room_code}].\n')
    return room
    
def print_room_status(room):
    print(f'Connected clients in room [{room.get_room_code()}]:',
          f'{len(room.get_client_list())}')
    for idx, client_obj in enumerate(room.get_client_list()):
        print(f'Client {idx+1}: [{client_obj.get_username()},',
              f'{client_obj.get_address()}]')
    print('')
    return

def print_info_when_client_enter_room(address, username, clients, 
                                      room_code, rooms, max_client_count):
    print(f'Accepted connection request from Client on [{address}].')
    print(f'With Username: [{username}], room code: [{room_code}].')
    print('All connected clients: ',
         f'[{len(clients)}/{max_client_count}]')
    room = [r for r in rooms if r.get_room_code() == room_code][0]
    print_room_status(room)
    return
