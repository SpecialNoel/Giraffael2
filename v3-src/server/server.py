# server.py

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
msgList = {}

class EncryptedMsg(BaseModel):
    senderID: str
    recipientID: str
    cipherText: str
    nonce: str

@app.post('/send')
async def send_msg(msg: EncryptedMsg):
    if msg.recipientID not in msgList:
        msgList[msg.recipientID] = []
    
    msgList[msg.recipientID].append(msg.model_dump())
    print(f"Stored for {msg.recipientID}: {msgList[msg.recipientID]}")
    return {'status': 'stored'}

@app.get('/fetch/{recipientID}')
async def fetch_msg(recipientID: str):
    msgs = msgList.pop(recipientID, [])
    return {'messages': msgs}

if __name__=='__main__':
    uvicorn.run(app, host='10.0.0.33', port=5001)
