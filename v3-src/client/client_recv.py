# client_recv.py

import requests
import base64
from encryption import decrypt

key = b'1234567890abcdef12345678'

response = requests.get('http://10.0.0.33:5001/fetch/Fish')
print(response.status_code)

try:
    data = response.json()
    msgs = data.get('messages', [])
except ValueError as e:
    print(f'Invalid JSON: {response.text}')
    msgs = []

for msg in msgs:
    cipherText = base64.b64decode(msg['cipherText'])
    nonce = base64.b64decode(msg['nonce'])
    plainText = decrypt(key, cipherText, nonce)
    print(f'From {msg['senderID']}: {plainText.decode()}')
