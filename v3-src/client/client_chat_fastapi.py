# client_chat_fastapi.py

# python v3-src/client/client_chat_fastapi.py

import base64
import requests
import sys
from encryption import encrypt, decrypt

# FastAPI logic for sending a message to a target client
def send(uri, senderID, recipientID, key, plainText):
    encryptedText = encrypt(key, plainText)
    # base64.b64encode() turns binary bytes into base64 bytes, and
    # decoding base64 bytes gives us an UTF-8 string, the supported format in JSON.
    cipherTextStr = base64.b64encode(encryptedText['cipherText']).decode()
    nonceStr = base64.b64encode(encryptedText['nonce']).decode()
    payload = {
        'typeOfMsg': 'message',
        'senderID': senderID,
        'recipientID': recipientID,
        'cipherText': cipherTextStr,
        'nonce': nonceStr
    }
    response = requests.post(uri+'send', json=payload)
    print(f'Received status from server: {response.json()}')
    return

# FastAPI logic for fetching a message as a receiver client
def recv(uri, recipientID, key):
    response = requests.get(uri+'fetch/'+recipientID)
    print(f'Response status code: {response.status_code}')
    try:
        data = response.json()
        messages = data.get('messages', [])
    except ValueError:
        print(f'Invalid JSON: {response.text}')
        messages = []
    for message in messages:
        senderID = message['senderID']
        cipherText = base64.b64decode(message['cipherText'])
        nonce = base64.b64decode(message['nonce'])
        plainText = decrypt(key, cipherText, nonce).decode()
        print(f'From {senderID}: {plainText}')
    return

if __name__=='__main__':
    uri = 'http://10.0.0.33:5001/'
    senderID = 'Dodo'
    recipientID = 'Fish'
    key = b'1234567890abcdef12345678'
    plainText = b'This is a plain text message.'
    
    choice = sys.argv[1]
    
    if choice == 'send':
        send(uri, senderID, recipientID, key, plainText)
    elif choice == 'recv':
        recv(uri, recipientID, key)
    else:
        print('Invalid argument passed when executing client_chat_fastapi.py')
