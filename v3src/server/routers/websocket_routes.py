# websocket_routes.py

from fastapi import APIRouter, WebSocket
from v3src.server.services.connection_manager import manager

router = APIRouter()

# WebSocket endpoint that acts like listen() and accept() in python socket
@router.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    