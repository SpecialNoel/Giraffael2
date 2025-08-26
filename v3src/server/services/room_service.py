# room_service.py

from v3src.server.database.room_ops.create_op import create_room
from v3src.server.database.msg_ops.general_op import room_code_exists_in_collection
from v3src.server.schemas.room import Room

def create_room_with_room_code(roomCode: str, roomList: list):
    try:
        create_room(roomCode)
        newRoom = Room(roomCode)
        roomList.append(newRoom)
        return {'status': 'success'} 
    except:
        return {'status': 'failed'}

def join_room_with_room_code(roomCode: str, roomList: list): 
    # Check if the given room code is in local cache room list first
    if roomCode not in roomList:
        print(f'Client tried to join a non-existing room [{roomCode}].')
        return {'status': 'failed'}
    
    # Check if the given room code corresponds to a room in database
    if not room_code_exists_in_collection(roomCode):
        print(f'Error in join_room(). Room [{roomCode}] does not exist in database.')
        return {'status': 'failed'}
    
    # Find the exist room from room list
    room = None
    for tempRoom in roomList:
        if tempRoom.get_room_code() == roomCode:
            room = tempRoom
            break
    
    if room is None:
        print(f'Error in join_room(). Room [{roomCode}] does not exist in room list.')
        return {'status': 'failed'}
    
    # Add the client to the target room
    room.add_client_to_client_list(clientSocket) # problem
    return {'status': 'success'}
