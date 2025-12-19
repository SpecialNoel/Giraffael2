# message_security.py

import base64
import websockets
import json
from client.crypto.encrypt_decrypt import encrypt, decrypt

# WebSocket logic for sending a message to a target client
async def chat_send_with_encryption(wsUri, senderID, recipientID, key, plainText):
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
async def chat_recv_with_decryption(wsUri, recipientID, key):
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