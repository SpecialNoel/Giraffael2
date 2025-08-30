# room_service.py

import uuid
from fastapi import WebSocket
from v3src.server.mongo_db.room_ops.create_op import create_room_in_db
from v3src.server.mongo_db.room_ops.check_op import check_room_existence
from v3src.server.schemas.room import Room

def create_room_with_room_code(room_code: str, uuid: str, username: str):
    # Create a room in MongoDB with given room code
    return create_room_in_db(room_code, uuid, username)

def join_room_with_room_code(roomCode: str): 
    
    return 
