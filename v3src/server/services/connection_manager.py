# connection_manager.py

import redis.asyncio as redis
from fastapi import WebSocket
from v3src.server.services.client_service import (connect_with_client, 
                                                  disconnect_from_client, 
                                                  disconnect_all_clients_from_a_room)

class ConnectionManager:
    def __init__(self, redisURL='redis://localhost:6379'):
        # room_code -> uuid -> {WebSocket, username}
        self.active: dict[str, dict[str, dict[WebSocket, str]]] = {}
        self.redisURL = redisURL
        self.redis = None
        self.TIME_THRESHOLD = 20
        self.MAX_USER_CAPACITY_PER_ROOM = 50
        
    # Connect to Redis and sub to the channel
    async def start(self):
        try: 
            self.redis = await redis.from_url(self.redisURL, decode_responses=True)
            print('Connected to Redis.')
        except:
            print('Failed to connect to Redis')
        return

    # Stop Pub/Sub listener and close Redis connection    
    async def stop(self):        
        if self.redis:
            for room_code in self.active:
                await self.disconnect_all(room_code)
                await self.delete_room(room_code)
            await self.redis.close()
            print('Server disconnected from Redis.')
    
    # Connect the client with a generated uuid, received username and socket
    async def connect(self, websocket: WebSocket):
        return await connect_with_client(self.redis, self.active, websocket, self.TIME_THRESHOLD)
    
    # Disconnect client by removing it from local cache, 
    #   closing the connection to its socket, and removing it from Redis.
    async def disconnect(self, uuid, room_code):
        return await disconnect_from_client(self.redis, self.active, uuid, room_code)
    
    # Disconnect all clients from a given room.
    async def disconnect_all(self, room_code):
        return await disconnect_all_clients_from_a_room(self.redis, self.active, room_code)

# A singleton that is used to share stored resources over functions in different scripts
# With Redis, data values like chat msg can be shared across multiple workers/service instances.
manager = ConnectionManager()
