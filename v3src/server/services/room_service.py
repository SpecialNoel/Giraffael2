# room_service.py

from v3src.server.database.room_ops.create_op import create_room
from v3src.server.database.room_ops.join_op import join_room
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
    # Check if the given roomCode is in local cache room list first
    if roomCode not in roomList:
        print(f'Client tried to join a non-existing room [{roomCode}].')
        return {'status': 'failed'}
    
    # Check if the given roomCode is corresponding to a room stored in database
    if join_room(roomCode):
        room = None
        for tempRoom in roomList:
            if tempRoom.get_room_code() == roomCode:
                room = tempRoom
                break
        room.add_client_to_client_list(clientSocket) # problem
        return {'status': 'success'}
    else: 
        return {'status': 'failed'}
