# connection_manager.py

import json
import asyncio
import redis.asyncio as redis
from datetime import datetime, timezone
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from v3src.server.mongo_db.client_ops.check_op import check_client_existence_in_db
from v3src.server.schemas.definitions import Message
from v3src.server.services.service_switch import handle_incoming_message

class ConnectionManager:
    def __init__(self, redisURL='redis://localhost:6379'):
        # room_code -> uuid -> {WebSocket, username}
        self.active: dict[str, dict[str, dict[WebSocket, str]]] = {}
        self.redisURL = redisURL
        self.redis = None
        self.TIME_THRESHOLD = 20
        
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
                await self.disconnect_all_clients_from_a_room(room_code)
                await self.delete_room(room_code)
            await self.redis.close()
            print('Server disconnected from Redis.')
    
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
        def get_client_info(websocket):
            room_code = websocket.query_params.get('room_code')
            uuid = websocket.query_params.get('uuid')
            username = websocket.query_params.get('username')
            return room_code, uuid, username
        
        async def check_if_client_info_match_in_db(room_code, uuid, username):
            check_client_existence_result = await check_client_existence_in_db(room_code, uuid, username)
            if not check_client_existence_result:
                data = {
                    'message': f'Failed to connect to server. Client [{uuid}] does not exist in DB.',
                    'status': 'failed',
                   }
                await websocket.send_text(json.dumps(data))
                return
            
        async def safe_task(task):
            try:
                await task
            except Exception as e:
                print(f'Task failed: {e}.')
        
        try: 
            # Accept the connection established by client
            await websocket.accept()
            
            # Get room code, uuid and username inputted by the client
            room_code, uuid, username = get_client_info(websocket)
            
            # Check if received room code, uuid and username match in MongoDB
            await check_if_client_info_match_in_db(room_code, uuid, username)
            print('Client info matched.')
            
            # Initialize the room if it is not yet existed in active client list
            if room_code not in self.active:
                self.active[room_code] = {}
            
            # Add this client to active client list (local cache)
            self.active[room_code][uuid] = {'websocket': websocket, 'username': username}
            print('Added client to local active client list.')
            
            # Add this client to Redis
            await self.redis.sadd(f'room_code:{room_code}:client_list', str(uuid))
            print('Added client to Redis.')
            
            # Print clients that are currently connected to Redis
            current_client_list = await self.redis.smembers(f'room_code:{room_code}:client_list')
            print(f'Current clients in room [{room_code}] in redis:', current_client_list)
            
            # Server sends a succeeded status to the client
            data = {
                    'message': f'Successfully connected to server.',
                    'status': 'succeeded',
                   }
            await websocket.send_text(json.dumps(data))
            print(f'Client [{uuid}] connected.')
            
            # Keep connection alive and forward incoming messages to other functions
            while True:
                try:
                    raw_msg = await asyncio.wait_for(websocket.receive_text(), timeout=self.TIME_THRESHOLD)
                    msg = json.loads(raw_msg)
                    
                    if msg.get('type') == 'pong':
                        # In Redis, set 'presence' of this uuid to 'online', which times out after self.TIME_THRESHOLD*2 seconds
                        await self.redis.setex(f'presence:{room_code}:{uuid}', self.TIME_THRESHOLD*2, 'online')
                    else: 
                        asyncio.create_task(safe_task(handle_incoming_message(uuid, room_code, raw_msg)))
                except asyncio.TimeoutError:
                    # Heartbeat: if no message received within self.TIME_THRESHOLD, send a ping to client
                    await websocket.send_json({'type': 'ping'})
                    print(f'Sent ping to [{uuid}] in room [{room_code}].')
        except WebSocketDisconnect:
            print(f'Client [{uuid}] disconnects from server.')
        except:
            print(f'Error in connection with [{uuid}].')
            # Server sends a failed status to the client
            data = {
                'message': f'Client encountered error when connecting to server.',
                'status': 'failed'
            }
            await websocket.send_text(json.dumps(data))
        finally:
            # Clean up client when it disconnects in any mean
            await self.disconnect(uuid, room_code)
        return

    # Get the online status of clients in Redis
    async def get_online_status_of_clients_in_room(self, room_code):
        # Get all uuids from the given room in Redis
        uuids = await self.redis.smembers(f'room_code:{room_code}:client_list')
        result = {}
        for uuid in uuids:
            presence = await self.redis.get(f'presence:{room_code}:{uuid}')
            result[uuid] = 'online' if presence else 'offline'
        return result

    async def disconnect(self, uuid: str, room_code: str):
        # Remove client from active client list (local cache)
        if room_code in self.active and uuid in self.active[room_code]:
            websocket = self.active[room_code][uuid]['websocket']
            
            # Close the client socket if it is not yet closed by client side
            if websocket.client_state != WebSocketState.DISCONNECTED:
                try:
                    await websocket.close()
                except:
                    pass
            del self.active[room_code][uuid]
            print('Removed client from local active client list.')
            
            # Remove the room from the active client list if the room becomes empty
            if not self.active[room_code]:
                del self.active[room_code]
                print('Removed empty room.')
        
        # Remove client from Redis
        await self.redis.srem(f'room_code:{room_code}:client_list', uuid)
        await self.redis.delete(f'presence:{room_code}:{uuid}')
        print(f'Client [{uuid}] removed from connection manager.')
        return
    
    async def disconnect_all_clients_from_a_room(self, room_code):
        if room_code in self.active:
            # Get a copy of uuids
            uuids = list(self.active[room_code].keys())
            
            # Remove every client from active client list (local cache)
            for uuid in uuids:
                del self.active[room_code][uuid]
        
            # Remove the room from the active client list if the room becomes empty
            if not self.active[room_code]:
                del self.active[room_code]
                print('Removed empty room.')
                
            # Remove all clients in the given room from Redis
            if uuids:
                await self.redis.srem(f'room_code:{room_code}:client_list', *uuids)
                print(f'Removed all clients in room [{room_code}] from Redis.')
                
            current = await self.redis.smembers(f'room_code:{room_code}:client_list')
            print('After removing the client, Redis status: ', current)
                
            print(f'Removed all clients from room [{room_code}].')
            return
        
    # Delete the room in Redis (useful for removing 'zombie clients')
    async def delete_room(self, room_code):
        await self.redis.delete(f'room_code:{room_code}:client_list')
        print(f'Deleted room [{room_code}] in Redis.')
        return        

# A singleton that is used to share stored resources over functions in different scripts
# With Redis, data values like chat msg can be shared across multiple workers/service instances.
manager = ConnectionManager()
