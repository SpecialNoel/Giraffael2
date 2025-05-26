# group_messaging_related.py

# This is the fourth step of achieving E2EE in asynchronous group messaging.
# Functions here handle group messaging (i.e. messaginig over a chatroom). 

import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# -----------------------------------------------------------------------------
# Helper functions: 

# Serialize ed25519 public key
def serialize_ed25519_public_key(key: ed25519.Ed25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
# Deserialize ed25519 public key
def deserialize_ed25519_public_key(data: bytes) -> ed25519.Ed25519PublicKey:
    return ed25519.Ed25519PublicKey.from_public_bytes(data)

# -----------------------------------------------------------------------------
'''
# Workflow:
When a client sends a message to a room, they:
    1. Use their senderKey to encrypt the message.
    2. Use their senderSigningPrivateKey to sign the encrypted message + nonce.
    3. Attach their senderSigningPublicKey (or have it cached by peers) so others can verify.
When another client receives that message, they:
    1. Look up the sender's senderSigningPublicKey from cache (from cache_sender_key())
    2. Use it in verify_signature() to authenticate the message.
'''

# Step 4.1: For the sender client: generate sender key and sender signing key
# senderSigningPublicKey of the sender client should be shared to all other clients:
#   1. On the first msg sent by this sender client,
#   2. When the senderKey is rotated.
# Note: The senderKey should be rotated periodically after N msgs or when a client joins/leaves. 
#       After rotation of senderKey, need to encrypt it for each recipient using DR sessions.
def generate_senderKey_and_senderSigningKey():
    senderKey = AESGCM.generate_key(bit_length=256)
    senderSigningPrivateKey = ed25519.Ed25519PrivateKey.generate()
    senderSigningPublicKey = senderSigningPrivateKey.public_key()
    return senderKey, senderSigningPrivateKey, senderSigningPublicKey

# Note: Step 4.2 needs to be executed only once per session, or on key rotation
# Step 4.2.1: Sender client encrypts its own sender key for each of the receiving clients in the room.
def encrypt_senderKey_for_each_recipient(senderKey, sessionKeysWithRecipients):
    # A list containing info held by the sender client about 
    #   encryptedSenderKey and corresponding nonce for each receiver client
    encryptedSenderKeys = {}
    # Encrypt senderKey for each receiver client using their pairwise session key
    for recipientID, sessionKey in sessionKeysWithRecipients.items():
        aesgcm = AESGCM(sessionKey)
        nonce = os.urandom(12)
        encryptedSenderKey = aesgcm.encrypt(nonce, senderKey, None)
        encryptedSenderKeys[recipientID] = {
            'encryptedSenderKey': encryptedSenderKey, 
            'nonce': nonce
        }
    return encryptedSenderKeys
# Step 4.2.2: Sender client sends the encryptedSenderKey to all other clients in the room
def get_combined_info_for_senderKey_to_send(roomID, senderID, encryptedSenderKey, 
                                            nonce, senderSigningPublicKey):
    return {
        'roomID': roomID,
        'senderID': senderID,
        'encryptedSenderKey': encryptedSenderKey,
        'nonce': nonce,
        'senderSigningPublicKey': serialize_ed25519_public_key(senderSigningPublicKey)
    }
# Step 4.2.3: Receiver clients decrypt encryptedSenderKey received from sender client
def decrypt_senderKey(encryptedSenderKey, nonce, sessionKey):
    # The encryptedSenderKey is decrypted to senderKey using sessionKey shared with the sender client
    aesgcm = AESGCM(sessionKey)
    # Note: Receiver clients need to cache decrypted senderKey in 'senderKeyCache'
    return aesgcm.decrypt(nonce, encryptedSenderKey, None) # decrypted senderKey
# Step 4.2.4: Receiver clients deserialize senderSigningPublicKey (currently in public bytes form) received from sender client
def deserialize_senderSigningPublicKey(senderSigningPublicKeyBytes):
    # Note: Receiver clients need to cache senderSigningPublicKey in 'senderKeyCache'
    return deserialize_ed25519_public_key(senderSigningPublicKeyBytes) # senderSigningPublicKey

# Step 4.3: Encrypt plain msg with sender key
def encrypt_msg_with_senderKey(senderKey, plainMsg):
    aesgcm = AESGCM(senderKey)
    # Note: Nonce used here is no secret, but it is needed for integrity and correctness
    # Nonce must be unique per msg
    nonce = os.urandom(12)
    return aesgcm.encrypt(nonce, plainMsg, None), nonce # encryptedMsg, nonce

# Step 4.4: Sign the signature of the encrypted msg; used by the sender client
# Note: Added nonce when signing to protect msg replay if someone reuses encryptedMsg with a new nonce.
def sign_encrypted_msg_with_senderSigning_key(senderSigningPrivateKey, nonce, encryptedMsg):
    payload = nonce + encryptedMsg
    return senderSigningPrivateKey.sign(payload) # signature for this msg encryption

# Step 4.5: Sender client sends these info to all other client in the room
def get_combined_info_for_msg_to_send(roomID, senderID, encryptedMsg, nonce, 
                                      signature, msgCounter, senderSigningPublicKey=None):
    # Note: msgCounter is used for better protection from replay attacks.
    # Note: Needs to include senderSigningPublicKey, but only if it is not already be cached by receiving clients.
    messageToSend = {
        'roomID': roomID,
        'senderID': senderID,
        'counter': msgCounter,
        'message': encryptedMsg, 
        'nonce': nonce,
        'signature': signature
    }
    if senderSigningPublicKey:
        messageToSend['senderSigningPublicKey'] = serialize_ed25519_public_key(senderSigningPublicKey)
    return messageToSend

# Step 4.6: For all clients: need to keep a local cache of sender keys of all other clients in the room.
# Needs to cache senderKey and senderSigningPublicKey to senderKeyCache once a client receives it from another client.
def cache_senderKey(roomID, senderID, senderKey, senderSigningPublicKey, senderKeyCache):
    if roomID not in senderKeyCache:
        senderKeyCache[roomID] = {}
    
    senderKeyCache[roomID][senderID] = {
        'senderKey': senderKey,
        'senderSigningKey': senderSigningPublicKey,
        'counter': 0
    }
    return senderKeyCache

# Step 4.7: Fetch the sender client's sender info for msg decryption; used by the receiver clients
# Needs to fetch the sender clinet's senderKey and senderSigningPublicKey from senderKeyCache 
#   when the receiver client wants to decrypt the msg sent by that sender client.
def get_cached_sender_key(roomID, senderID, senderKeyCache):
    return senderKeyCache.get(roomID, {}).get(senderID, None)

# Step 4.8: Signature verification; used by the receiver clients
def verify_signature(senderSigningPublicKey, nonce, encryptedMsg, signature):
    payload = nonce + encryptedMsg
    try:
        senderSigningPublicKey.verify(signature, payload)
        return True
    except:
        return False

# Step 4.9: Decrypt encrypted msg with cached sender key; used by the receiver clients
def decrypt_msg_with_cached_senderKey(roomID, senderID, msgCounter, encryptedMsg, 
                                      nonce, signature, senderKeyCache):
    # One entry has three properties: senderKey, senderSigningKey, and counter.
    senderKeyCacheEntry = get_cached_sender_key(roomID, senderID, senderKeyCache)
    if senderKeyCacheEntry:
        # Check the msg counter for replay attack protection
        if msgCounter <= senderKeyCacheEntry['counter']:
            raise Exception('Replay attack detected in decrypt_msg_with_cached_senderKey()')
        senderKeyCacheEntry['counter'] = msgCounter
        
        # Verify signature
        if not verify_signature(senderKeyCacheEntry['senderSigningKey'], nonce, encryptedMsg, signature):
            raise Exception('Invalid signature detected in decrypt_msg_with_cached_senderKey()')
        
        # Decrypt for plain msg using sender client's senderKey
        aesgcm = AESGCM(senderKeyCacheEntry['senderKey'])
        return aesgcm.decrypt(nonce, encryptedMsg, None) # decryptedMsg
