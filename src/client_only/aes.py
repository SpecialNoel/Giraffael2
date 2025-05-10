# aes.py

# This file contains methods needed to implement AES part of E2EE.
# The AES-256 GCM is used here fore secure encryption of data.
# The GCM mode is used as it performs better than the CBC mode.

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

# aesKey: generated using ECDH
# data: bytes object
def encrypt_data_with_aes_gcm(aesKey, data):
    nonce = get_random_bytes(12) # generate a unique 12 bytes nonce for EACH encryption
    cipher = AES.new(aesKey, AES.MODE_GCM, nonce=nonce)
    encryptedData, tag = cipher.encrypt_and_digest(data) # tag is a MAC tag
    return nonce, encryptedData, tag

# aesKey: generated using ECDH
# nonce: random bytes object
# encryptedData: encrypted bytes object
# tag: MAC tag, used to authenticate encryptedData
def decrypt_data_with_aes_gcm(aesKey, nonce, encryptedData, tag):
    cipher = AES.new(aesKey, AES.Mode_GCM, nonce=nonce)
    decryptedData = cipher.decrypt_and_verify(encryptedData, tag)
    return decryptedData
