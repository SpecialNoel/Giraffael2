# websocket_routes.py

from fastapi import APIRouter, WebSocket
from v3src.server.services.connection_manager import manager

router = APIRouter()

# WebSocket endpoint that acts like listen() and accept() in python socket
@router.websocket('/ws/{username}')
async def websocket_endpoint(websocket: WebSocket, username: str):
    await manager.connect(username, websocket)
    