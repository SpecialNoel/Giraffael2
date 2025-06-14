# encryption.py

import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Encrypt a plain text with AESGCM and a 12 bytes random nonce
def encrypt(key: bytes, plainText: bytes) -> dict:
    aesgcm = AESGCM(key)
    nonce = os.urandom(12)
    cipherText = aesgcm.encrypt(nonce, plainText, None)
    return {'cipherText': cipherText, 'nonce': nonce}

# Decrypt a cipher text with AESGCM and the same nonce used for the encryption
def decrypt(key: bytes, cipherText: bytes, nonce: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, cipherText, None) # plainText: bytes
    