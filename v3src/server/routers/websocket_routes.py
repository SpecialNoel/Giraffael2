# websocket_routes.py

from fastapi import APIRouter, WebSocket
from v3src.server.services.websocket_service import websocket_action

router = APIRouter()

# WebSocket endpoint that acts like listen() and accept() in python socket
@router.websocket('/ws/{username}')
async def websocket_endpoint(websocket: WebSocket, username: str):
    return await websocket_action(websocket, username)
