# room_routes.py

from fastapi import APIRouter
from v3src.server.services.room_service import create_room_with_room_code, join_room_with_room_code

router = APIRouter()
roomList = [] # local cache of list of rooms

# FastAPI endpoint for handling a 'create room' request from a client
@router.post('/room/create/{roomCode}')
def create_room(roomCode: str):
    return create_room_with_room_code(roomCode, roomList)

# FastAPI endpoint for handling a 'join room' request from a client
@router.post('/room/join/{roomCode}')
def create_room(roomCode: str):
    return join_room_with_room_code(roomCode, roomList)
