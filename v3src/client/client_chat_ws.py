# client_chat_ws.py

# python v3src/client/client_chat_ws.py

import asyncio
import base64
import json
import sys
import websockets
from v3src.client.encryption import encrypt, decrypt

# WebSocket logic for sending a message to a target client
async def chat_send(wsUri, senderID, recipientID, key, plainText):
    encryptedText = encrypt(key, plainText)    
    cipherTextStr = base64.b64encode(encryptedText['cipherText']).decode()
    nonceStr = base64.b64encode(encryptedText['nonce']).decode()
    
    wsUriWithSenderID = wsUri + senderID
    async with websockets.connect(wsUriWithSenderID) as websocket:
        msg = {
            'typeOfMsg': 'message',
            'senderID': senderID, 
            'recipientID': recipientID,
            'cipherText': cipherTextStr,
            'nonce': nonceStr
        }
        await websocket.send(json.dumps(msg))

        # After sending a message to the target client, start receiving messages
        # while True:
        #     response = await websocket.recv()
        #     print('Received response:', response)
    return
            
# WebSocket logic for continuously receiving messages as a receiver client
async def chat_recv(wsUri, recipientID, key):
    wsUriWithRecipientID = wsUri + recipientID
    async with websockets.connect(wsUriWithRecipientID) as websocket:
        while True:
            response = await websocket.recv()
            # print('Received response:', response)

            # response.get() returns a string. Must parse it into a JSON object
            #  before accessing its fields
            message = json.loads(response)
            senderID = message['senderID']
            cipherText = base64.b64decode(message['cipherText'])
            nonce = base64.b64decode(message['nonce'])
            plainText = decrypt(key, cipherText, nonce).decode()
            print(f'Received from {senderID}: {plainText}')
    return

if __name__=='__main__':
    # Shared info
    wsUri = 'ws://10.0.0.33:5001/ws/'
    key = b'1234567890abcdef12345678'
    
    choice = sys.argv[1]
    print(f'choice: {choice}')
    
    if choice == 'recv':
        # Receiver client:
        asyncio.run(chat_recv(wsUri, 'Fish', key))
    elif choice == 'send':
        # Sender client:
        plainText = b'This is a plain text message.'
        asyncio.run(chat_send(wsUri, 'Dodo', 'Fish', key, plainText))
    else:
        print('Invalid argument passed when executing client_chat_ws.py')
