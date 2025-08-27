# websocket_service.py

import json
from fastapi import WebSocket
from v3src.server.schemas.client_obj import Client_Obj

async def websocket_action(websocket: WebSocket, username: str):
    try: 
        # Accept the client with the dedicated websocket and update clientList
        await websocket.accept()
        
        clientHost, clientPort = websocket.client
        
        # Now server has accepted client socket
        clientObj = Client_Obj(socket=websocket,
                            address=clientHost, 
                            username=username)
        
        # Server sends a success status to the client
        payload = {
            'status': 'success'
        }
        await websocket.send_text(json.dumps(payload))
        
        # Return this 
    except Exception as e:
        print(f'Error in websocket_action(): {e}.')
        # Server sends a failed status to the client
        payload = {
            'status': 'failed'
        }
        await websocket.send_text(json.dumps(payload))
    return  
