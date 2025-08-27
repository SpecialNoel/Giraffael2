# connection_manager.py

from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active: dict[str, WebSocket] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active[user_id] = websocket

    def disconnect(self, user_id: str):
        self.active.pop(user_id, None)

    async def send_json(self, user_id: str, payload: dict):
        websocket = self.active.get(user_id)
        if websocket:
            await websocket.send_text(json.dumps(payload))

manager = ConnectionManager()