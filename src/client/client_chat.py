# client_chat.py

# python -m src.client.client_chat

import asyncio
import uuid
from src.client.transport.websocket_client import connect

if __name__=='__main__':    
    server_ip = 'Giraffael.com' # domain for Giraffael
    base_http_uri = f'http://{server_ip}:5001/'
    base_ws_uri = f'ws://{server_ip}:5001/ws'
    
    client_for_testing = {
        'username': 'dodo',
        'room_code': 'fWpO003k8b2',
        'client_uuid': uuid.uuid4()
    }
    asyncio.run(connect(base_ws_uri, client_for_testing.room_code, 
                        client_for_testing.client_uuid, client_for_testing.username))
    