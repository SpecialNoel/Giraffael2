# recv_msg.py

import json
import websockets

async def receive_msg(websocket):
    try:
        async for raw_msg in websocket:
            msg = json.loads(raw_msg)
            
            if msg.get('type') == 'ping':
                # Handle ping signal by sending back a pong to server 
                await websocket.send(json.dumps({'type': 'pong'}))
                print('\nSent pong to server')
            else:
                # Handle other messages
                await handle_incoming_message(msg)
    except websockets.ConnectionClosed:
        print('Connection closed by server.')
    except Exception as e:
        print(f'Unexpected error in recv_heartbeat(): {e}.')
        
async def handle_incoming_message(msg):
    print('In handle_incoming_message().')
    print(f'Received unexpected msg in recv_heartbeat(): [{msg}]')
    return