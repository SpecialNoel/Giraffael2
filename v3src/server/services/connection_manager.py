# connection_manager.py

import json
import asyncio
import redis.asyncio as redis
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect
from v3src.server.mongo_db.client_ops.check_op import check_client_existence_in_db
from v3src.server.mongo_db.client_ops.delete_op import delete_client_from_redis
from v3src.server.schemas.definitions import Message

class ConnectionManager:
    def __init__(self, redisURL='redis://localhost:6379'):
        # room_code -> {uuid, WebSocket, username}
        self.active: dict[str, dict[str, WebSocket, str]] = {}
        self.redisURL = redisURL
        self.redis = None
        self.pubsub_task = None
        
    # Connect to Redis and sub to the channel
    async def start(self):
        try: 
            self.redis = await redis.from_url(self.redisURL, decode_responses=True)
            print('Connected to Redis.')
        except:
            print('Failed to connect to Redis')
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
    
    # Redis subscribes to channel (NOT client subscribe to channel)
    async def subscribe_to_channel(self, room_code):
        async def broadcast(room_code, msg_obj: Message):
            clients = self.active.get(room_code, {})
            for uuid, info in clients.items():
                try:
                    await info['websocket'].send_json(msg_obj.model_dump())
                    print(f'Sent json message to client [{uuid}].')
                except Exception as e:
                    print(f'Failed to send json message to client [{uuid}]. Reason: {e}.')
        
        # Subscribe to channel
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(f'room_code:{room_code}:channel')
        
        # Note: 'async for' runs indefinitely as a background task.
        async for msg in pubsub.listen():
            # Handle msg (with type of dict, defaulted by pubsub.listen() returns)
            if msg['type'] == 'message':
                msg_obj = Message.model_validate_json(msg['data'].decode())
                await broadcast(room_code, msg_obj)
        return
    
    async def publish_to_channel(self, room_code, msg: Message):
        await self.redis.publish(f'room_code:{room_code}:channel', msg.model_dump_json())
        return     
    
    async def publish_chat_msg_to_channel(self, room_code, uuid, chat_msg):
        msg = Message(
            type='chat',
            room_code=room_code,
            sender=uuid,
            payload={'data': chat_msg},
            timestamp=datetime.now(tz=timezone.utc)
        )
        await self.publish_to_channel(room_code, msg)
        return

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
            check_client_existence_result = await check_client_existence_in_db(room_code, uuid, username)
            if not check_client_existence_result:
                data = {
                    'message': f'Failed to connect to server. Client [{uuid}] does not exist in DB.',
                    'status': 'failed',
                   }
                await websocket.send_text(json.dumps(data))
                return
            
            # Add this client to local cache
            self.active[room_code][uuid] = {'websocket': websocket, 
                                            'username': username}
            # Add this client to Redis
            await self.redis.sadd(f'room_code:{room_code}:client_list', uuid)
            # Print clients that are currently connected to Redis
            current_client_list = await self.redis.smembers(f'room_code:{room_code}:client_list')
            current_client_list = {client.decode() for client in current_client_list}
            print('Current clients in redis:', current_client_list)
            
            # Server sends a succeeded status to the client
            data = {
                    'message': f'Successfully connected to server.',
                    'status': 'succeeded',
                   }
            await websocket.send_text(json.dumps(data))
            print(f'Client [{uuid}] connected.')
        except Exception as e:
            print(f'Error in connection with [{uuid}]: {e}.')
            # Server sends a failed status to the client
            data = {
                'message': f'Client encountered error when connecting to server.',
                'status': 'failed'
            }
            await websocket.send_text(json.dumps(data))
        return
 
    async def disconnect(self, uuid: str, room_code: str):
        # Remove client from local cache
        self.active.pop(uuid, None)
        # Remove client from Redis
        await self.redis.srem(f'room_code:{room_code}:client_list', uuid)
        print(f'Client [{uuid}] removed from connection manager.')
        return
    
# A singleton that is used to share stored resources over functions in different scripts
# With Redis, data values like chat msg can be shared across multiple workers/service instances.
manager = ConnectionManager()
