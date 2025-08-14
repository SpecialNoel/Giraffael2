# websocket_routes.py

from fastapi import APIRouter, WebSocket
from v3src.server.services.websocket_service import websocket_action

router = APIRouter()
clientList = {}

# WebSocket endpoint that acts like listen() and accept() in python socket
@router.websocket('/ws/{clientID}')
async def websocket_endpoint(websocket: WebSocket, clientID: str):
    return await websocket_action(websocket, clientID, clientList)
