# websocket_service.py

from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect

async def websocket_action(websocket: WebSocket, clientID: str, clientList: dict):
    # Accept the client with the dedicated websocket and update clientList
    await websocket.accept()
    clientList[clientID] = websocket
    
    try:
        # Message sending loop
        while True:
            # Wait and receive message and recipientID inputted by this client
            data = await websocket.receive_json()
            recipientID = data['recipientID']
            if recipientID in clientList:
                # If the recipient client is online (not disconnected), send the message to it
                await clientList[recipientID].send_json(data)
                print(f'{clientID} sent: {data}')
            else:
                # If the recipient client is offline (disconnected), do nothing
                print(f'{recipientID} offline. Store message: {data}.')
    except WebSocketDisconnect:
        # The client disconnected, remove it from clientList 
        del clientList[clientID]
    return  
