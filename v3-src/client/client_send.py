# client_send.py

import requests
import base64
from encryption import encrypt

key = b'1234567890abcdef12345678'
plainText = b'This is a plain text.'
encryptedText = encrypt(key, plainText)

# base64.b64encode() turns binary bytes into base64 bytes, and
# decoding base64 bytes gives us an UTF-8 string, the supported format in JSON.
cipherTextStr = base64.b64encode(encryptedText['cipherText']).decode()
NonceStr = base64.b64encode(encryptedText['nonce']).decode()
payload = {
    'senderID': 'Dodo',
    'recipientID': 'Fish',
    'cipherText': cipherTextStr,
    'nonce': NonceStr
}

response = requests.post('http://10.0.0.33:5001/send', json=payload)
print(response.json())
