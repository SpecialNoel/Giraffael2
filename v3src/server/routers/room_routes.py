# room_routes.py

from fastapi import APIRouter
from v3src.server.services.room_service import create_room_with_room_code, join_room_with_room_code

router = APIRouter()
roomList = [] # local cache of list of rooms

# FastAPI endpoint for handling a 'create room' request from a client
@router.post('/room/create/{roomCode}')
def create_room(roomCode: str):
    createRoomSuccess = create_room_with_room_code(roomCode, roomList)
    if createRoomSuccess['status'] == 'failed':
        print(f'Error in create_room(). Failed to create room [{roomCode}].')
    
    return join_room_with_room_code(roomCode, roomList)

# FastAPI endpoint for handling a 'join room' request from a client
@router.post('/room/join/{roomCode}')
def join_room(roomCode: str):
    return join_room_with_room_code(roomCode, roomList)
