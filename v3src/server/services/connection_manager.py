# connection_manager.py

import json
import asyncio
import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect
from v3src.server.mongo_db.client_ops.check_op import check_client_existence_in_db

class ConnectionManager:
    def __init__(self, redisURL='redis://localhost:6379'):
        # uuid -> username, socket, room_code
        self.active: dict[str, (str, WebSocket, str)] = {}
        self.redisURL = redisURL
        self.redis = None
        self.pubsub_task = None
        
    # Connect to Redis and sub to the channel
    async def start(self):
        # An example task of reading message from this subscribed channel
        # Replace this with other features of the project
        async def reader():
            async for msg in pubsub.listen():
                if msg["type"] == "message":
                    payload = json.loads(msg["data"])
                    uuid = payload["uuid"]
                    message = payload["message"]

                    ws = self.active.get(uuid)
                    if ws:
                        await ws.send_text(json.dumps(message))
        
        self.redis = await redis.from_url(self.redisURL, decode_responses=True)
        print('Connected to Redis.')
        pubsub = self.redis.pubsub()
        await pubsub.subscribe('channel')
        self.pubsub_task = asyncio.create_task(reader())
        print('Subscribed to READ task.')
        return
    
    async def stop(self):
        #Stop Pub/Sub listener and close Redis connection
        if self.pubsub_task:
            self.pubsub_task.cancel()
            try:
                await self.pubsub_task
                print('Stopped subscribing to READ task.')
            except asyncio.CancelledError:
                pass
        if self.redis:
            await self.redis.close()
            print('Disconnected from Redis.')

    # Connect the client with a generated uuid, received username and socket
    async def connect(self, websocket: WebSocket):
        try: 
            # Accept the connection established by client
            await websocket.accept()
            
            # Get room code and username inputted by the client
            room_code = websocket.query_params.get('room_code')
            uuid = websocket.query_params.get('uuid')
            username = websocket.query_params.get('username')
            
            # Check if received room code, uuid and username match in MongoDB
            if not check_client_existence_in_db(room_code, uuid, username):
                data = {
                    'message': f'Failed to connect to server. Client [{uuid}] does not exist in DB.',
                    'status': 'failed',
                   }
                await websocket.send_text(json.dumps(data))
                return
            
            # Add this client to the client list (local cache)
            self.active[uuid] = (username, websocket, room_code)
            
            # Server sends a succeeded status to the client
            data = {
                    'message': f'Successfully connected to server.',
                    'status': 'succeeded',
                   }
            await websocket.send_text(json.dumps(data))
            print(f'Client [{uuid}] connected.')
            
            # Keep receiving client input until client disconnects
            try:
                while True:
                    # These two lines does nothing, as things like join/leave room should
                    #   be already handled by FastAPI endpoints (HTTP).
                    data = await websocket.receive_text()
                    print(f'Received from client [{uuid}]: {data}')
            except WebSocketDisconnect: 
                print(f'Client [{uuid}] disconnected.')
                self.disconnect(uuid)
        except Exception as e:
            print(f'Error in connection with [{uuid}]: {e}.')
            # Server sends a failed status to the client
            data = {
                'message': f'Client encountered error when connecting to server.',
                'status': 'failed'
            }
            await websocket.send_text(json.dumps(data))
        return
 
    def disconnect(self, uuid: str):
        self.active.pop(uuid, None)
        print(f'Client [{uuid}] removed from connection manager.')
        return

    async def send_json(self, uuid: str, payload: dict):
        # Step 1: Send json locally
        websocket = self.active.get(uuid)[1]
        if websocket:
            await websocket.send_text(json.dumps(payload))

        # Step 2: Publish json to Redis to make other workers/servers send too
        if self.redis:
            msg = {'uuid': uuid, 'message': payload}
            await self.redis.publish('channel', json.dumps(msg))
        return

# A singleton that is used to share stored resources over functions in different scripts
# With Redis, it can be shared across multiple workers/service instances.
manager = ConnectionManager()
