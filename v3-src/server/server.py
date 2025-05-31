# server.py

# python v3-src/server/server.py

import uvicorn
from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel

app = FastAPI()
clientList = {} # Used in Websocket logic
msgList = {}    # Used in FastAPI logic

class EncryptedMsg(BaseModel):
    typeOfMsg: str
    senderID: str
    recipientID: str
    cipherText: str
    nonce: str

# Websocket logic that acts like listen() and accept() in python socket
@app.websocket('/ws/{clientID}')
async def websocket_endpoint(websocket: WebSocket, clientID: str):
    await websocket.accept()
    clientList[clientID] = websocket
    try:
        while True:
            data = await websocket.receive_json()
            recipientID = data['recipientID']
            if recipientID in clientList:
                await clientList[recipientID].send_json(data)
                print(f'{clientID} sent: {data}')
            else:
                print(f"{recipientID} offline. Store message: {data}.")
    except WebSocketDisconnect:
        del clientList[clientID]
    return       

# FastAPI logic for handling a 'send' request from a sender client
@app.post('/send')
async def send_msg(msg: EncryptedMsg):
    if msg.recipientID not in msgList:
        msgList[msg.recipientID] = []
    
    msgList[msg.recipientID].append(msg.model_dump())
    print(f'Stored for {msg.recipientID}: {msgList[msg.recipientID]}')
    return {'status': 'stored'}

# FastAPI logic for handling a 'fetch' request from a receiver client
@app.get('/fetch/{recipientID}')
async def fetch_msg(recipientID: str):
    msgs = msgList.pop(recipientID, [])
    return {'messages': msgs}

if __name__=='__main__':
    # Run a uvicorn web server
    uvicorn.run(app, host='10.0.0.33', port=5001)
