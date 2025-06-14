# server.py

# python -m v3src.server.main

import uvicorn
from fastapi import FastAPI, WebSocket, File, UploadFile
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel
from v3src.server.mongodb_related.room_ops.create_op import create_room
from v3src.server.mongodb_related.file_ops.list_op import get_fileID
from v3src.server.mongodb_related.file_ops.upload_op_fastapi import upload_file_with_fastapi
from v3src.server.mongodb_related.file_ops.download_op_fastapi import download_file_with_fastapi

# WebSocket: used for real-time message communication (e.g. message transmission, type indicator, msg 'read' indicator)
# FastAPI (HTTP): used for anything else (e.g. file transmission, chat history retrieval, chat room management, user authentication)

app = FastAPI()
clientList = {} # Used in WebSocket logic
msgList = {}    # Used in FastAPI logic

class EncryptedMsg(BaseModel):
    typeOfMsg: str
    senderID: str
    recipientID: str
    cipherText: str
    nonce: str

# WebSocket endpoint that acts like listen() and accept() in python socket
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
                print(f'{recipientID} offline. Store message: {data}.')
    except WebSocketDisconnect:
        del clientList[clientID]
    return  

# FastAPI endpoint for handling a 'join room' request from a client
@app.post('/join/{roomCode}')
def create_room_with_room_code(roomCode: str):
    try:
        create_room(roomCode)
    except:
        return {'status': 'failed'}
    return {'status': 'success'}

# FastAPI endpoint for handling a 'send' request from a sender client
@app.post('/send')
def send_msg(msg: EncryptedMsg):
    if msg.recipientID not in msgList:
        msgList[msg.recipientID] = []
    
    msgList[msg.recipientID].append(msg.model_dump())
    print(f'Stored for {msg.recipientID}: {msgList[msg.recipientID]}')
    return {'status': 'success'}

# FastAPI endpoint for handling a 'fetch' request from a receiver client
@app.get('/fetch/{recipientID}')
def fetch_msg(recipientID: str):
    msgs = msgList.pop(recipientID, [])
    return {'messages': msgs}

# FastAPI endpoint for handling a 'upload' request from a client
@app.post('/upload/{roomCode}')
def upload_file(roomCode: str, file: UploadFile = File(...)):
    upload_file_with_fastapi(roomCode, file)
    return {'status': 'success'}

# FastAPI endpoint for handling a 'download' request from a client
@app.get('/download/{roomCode}/{filename}')
def download_file_fastapi(roomCode: str, filename: str):
    fileID = get_fileID(filename, roomCode)
    if fileID == None:
        print(f'Error in download_file(): {fileID} is invalid.')
        return None

    return download_file_with_fastapi(roomCode, fileID)

if __name__=='__main__':
    # Run a uvicorn web server
    uvicorn.run(app, host='10.0.0.33', port=5001)
