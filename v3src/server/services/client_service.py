# client_service.py

import json
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from starlette.websockets import WebSocketState
from v3src.server.mongo_db.room_ops.check_op import check_client_existence_in_db
from v3src.server.services.message_service import handle_incoming_message

# Connect the client with a generated uuid, received username and socket
async def connect_with_client(redis, active, websocket: WebSocket, TIME_THRESHOLD):
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
        if room_code not in active:
            active[room_code] = {}
        
        # Add this client to active client list (local cache)
        active[room_code][uuid] = {'websocket': websocket, 'username': username}
        print('Added client to local active client list.')
        
        # Add this client to Redis
        await redis.sadd(f'room_code:{room_code}:client_list', str(uuid))
        print('Added client to Redis.')
        
        # Print clients that are currently connected to Redis
        current_client_list = await redis.smembers(f'room_code:{room_code}:client_list')
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
                raw_msg = await asyncio.wait_for(websocket.receive_text(), timeout=TIME_THRESHOLD)
                msg = json.loads(raw_msg)
                
                if msg.get('type') == 'pong':
                    # In Redis, set 'presence' of this uuid to 'online', which times out after TIME_THRESHOLD*2 seconds
                    await redis.setex(f'presence:{room_code}:{uuid}', TIME_THRESHOLD*2, 'online')
                else: 
                    asyncio.create_task(safe_task(handle_incoming_message(uuid, room_code, raw_msg)))
            except asyncio.TimeoutError:
                # Heartbeat: if no message received within TIME_THRESHOLD, send a ping to client
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
        await disconnect_from_client(redis, active, uuid, room_code)
    return 

# Disconnect client by removing it from local cache, 
#   closing the connection to its socket, and removing it from Redis.
async def disconnect_from_client(redis, active, uuid: str, room_code: str):
    # Remove client from active client list (local cache)
    if room_code in active and uuid in active[room_code]:
        websocket = active[room_code][uuid]['websocket']
        
        # Close the client socket if it is not yet closed by client side
        if websocket.client_state != WebSocketState.DISCONNECTED:
            try:
                await websocket.close()
            except:
                pass
        del active[room_code][uuid]
        print('Removed client from local active client list.')
        
        # Remove the room from the active client list if the room becomes empty
        if not active[room_code]:
            del active[room_code]
            print('Removed empty room.')
    
    # Remove client from Redis
    await redis.srem(f'room_code:{room_code}:client_list', uuid)
    await redis.delete(f'presence:{room_code}:{uuid}')
    print(f'Client [{uuid}] removed from connection manager.')
    return

# Disconnect all clients from a given room.
async def disconnect_all_clients_from_a_room(redis, active, room_code):
    if room_code in active:
        # Get a copy of uuids
        uuids = list(active[room_code].keys())
        
        # Remove every client from active client list (local cache)
        for uuid in uuids:
            del active[room_code][uuid]
    
        # Remove the room from the active client list if the room becomes empty
        if not active[room_code]:
            del active[room_code]
            print('Removed empty room.')
            
        # Remove all clients in the given room from Redis
        if uuids:
            await redis.srem(f'room_code:{room_code}:client_list', *uuids)
            print(f'Removed all clients in room [{room_code}] from Redis.')
            
        current = await redis.smembers(f'room_code:{room_code}:client_list')
        print('After removing the client, Redis status: ', current)
            
        print(f'Removed all clients from room [{room_code}].')
        return
