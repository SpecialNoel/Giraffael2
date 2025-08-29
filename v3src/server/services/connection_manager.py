# connection_manager.py

import json
import asyncio
import redis.asyncio as redis
from fastapi import WebSocket, WebSocketDisconnect
from v3src.server.schemas.client_obj import Client_Obj

class ConnectionManager:
    def __init__(self, redisURL='redis://localhost:6379'):
        # uuid -> username, socket
        self.active: dict[str, (str, WebSocket)] = {}
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
                    user_id = payload["user_id"]
                    message = payload["message"]

                    ws = self.active.get(user_id)
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
            username = websocket.query_params.get('username')
                    
            # Get client host address
            clientHost, clientPort = websocket.client
            
            # Generate client obj and the uuid for this client
            clientObj = Client_Obj(socket=websocket,
                                   address=clientHost, 
                                   username=username)
            uuid: str = clientObj.get_uuid()
            
            # Add this client to the client list
            self.active[uuid] = (username, websocket)
            
            # Server sends a success status to the client
            payload = {
                'status': 'success'
            }
            await websocket.send_text(json.dumps(payload))
            print(f'Client [{uuid}] connected.')
            
            # Keep receiving client input until client disconnects
            try:
                while True:
                    data = await websocket.receive_text()
                    print(f'Received from client [{uuid}]: {data}')
            except WebSocketDisconnect: 
                print(f'Client [{uuid}] disconnected.')
                self.disconnect(uuid)
            
        except Exception as e:
            print(f'Error in connection with [{clientHost}]: {e}.')
            # Server sends a failed status to the client
            payload = {
                'status': 'failed'
            }
            await websocket.send_text(json.dumps(payload))
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
