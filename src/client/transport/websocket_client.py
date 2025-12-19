# websocket_client.py

import asyncio
import websockets
import json
from src.client.transport.send_msg import (send_chat_message,
                                           send_create_room_request,
                                           send_disconnect_request)
from src.client.transport.recv_msg import receive_msg

async def connect(base_ws_uri, room_code, uuid, username, ):
    uri = base_ws_uri + f'?room_code={room_code}&uuid={uuid}&username={username}'
    print(f'uri: [{uri}].')
    
    # Client connects to server via WebSocket endpoint
    async with websockets.connect(uri) as websocket:        
        msg = await websocket.recv()
        data = json.loads(msg)
        print(f'Response from server: {data}')
        
        if data['status'] != 'succeeded':
            print('Failed to connect to server.')
            return
        print('Successfully connected to server.')
        
        # Start receiving heartbeat in the background
        receiver_thread = asyncio.create_task(receive_msg(websocket))
        sender_thread = asyncio.create_task(user_input_loop(websocket, room_code, uuid))
        
        # Wait until either finishes (either disconnects or error occurs)
        done, pending = await asyncio.wait(
            [receiver_thread, sender_thread],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel the unfinished tasks before stopping the client loop
        for task in pending:
            task.cancel()
        print('Client loop ended.')

async def send(type, http_uri=None, username=None, uuid=None, room_code=None, websocket=None, msg=None):
    if type == 'chat':
        send_chat_message(room_code, uuid, msg, websocket)
    elif type == 'create':
        send_create_room_request(http_uri, username, room_code)
    elif type == 'disconnect':
        send_disconnect_request(websocket)
    return

async def receive():
    return
