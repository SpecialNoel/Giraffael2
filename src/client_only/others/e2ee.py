# e2ee.py

# This file contains steps used to implement E2EE between clients with 
#   X3DH (for identification and authentication), and Double Ratchet (for 1-on-1 only).

# E2EE encrypts data so only the intended recipient can decrypt it 
#   (i.e. sending straight from sender client to receiver client(s), meaning that 
#   not even the server would be able to decrypt)

# Note: Database for key server should be only available for uploading and querying. 
#       Each client should only be able to upload their identity key once.
# Note: Only the trusted server should be able to query the key data. 
#       Clients should not be able to query MongoDB directly.

'''
Note: In database, only public keys should be stored. Also needs to prevent database injection attacks.
      The following information should be stored in the database:
        1. Identity public key   (validate before client uploading pre-key bundles)
        2. Signed public pre-key (validate on upload; deleted upon use)
        3. One-time pre-keys     (validate on upload; deleted upon use)
        4. Signatures
Note: The sender key should not be uploaded to the key server, as it is private and confidential.
      It is used to encrypt and authenticate msgs sent by its owner client to a room.
      The sender key should be shared only directly with other clients in the room.
'''

'''
Example for pre-key bundle:
{
  "userID": "alice123",
  "identityKey": "<base64 Curve25519 pubkey>",
  "signedPrekey": {
    "key": "<base64 Curve25519 pubkey>",
    "signature": "<base64 Ed25519 sig>"
  },
  "one_time_pre_keys": [
    {
      "keyID": "otk1",
      "key": "<base64 Curve25519 pubkey>",
      "used": false
    },
    ...
  ],
  "timestamp": "2025-05-21T10:00:00Z"
} 
'''

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Crypto.Random import get_random_bytes

# Step 1.1: Identity key (for client identification)
def generate_identity_key():
    # x25519 specifies the ECDH protocol, that uses the Curve25519 elliptic curve 
    #   to securely establish a shared secret between two parties
    identityPrivateKey = x25519.X25519PrivateKey.generate()
    identityPublicKey = identityPrivateKey.public_key()
    return identityPrivateKey, identityPublicKey

# Step 1.2: Signing key (for msg authentication)
def generate_signing_key():
    signingPrivateKey = ed25519.Ed25519PrivateKey.generate()
    signingPublicKey = signingPrivateKey.public_key()
    return signingPrivateKey, signingPublicKey

# Step 2.1: Pre-key bundle (for client registration)
def generate_signed_prekey():
    signedPrivatePrekey = x25519.X25519PrivateKey.generate()
    signedPublicPrekey = signedPrivatePrekey.public_key()
    return signedPrivatePrekey, signedPublicPrekey

# Step 2.2: Get signature of signed public pre-key
def get_signature_of_signed_prekey(signingPrivateKey, signedPublicPrekey):
    return signingPrivateKey.sign(signedPublicPrekey.public_bytes())
    
# Step 2.3: Get pre-key bundle (to be uploaded to key server for other clients to fetch)
# Note: This is mainly used for X3DH with other clients.
def get_prekey_bundle(identityPublicKey, signedPublicPrekey, signature):
    return {
        'identityKey': identityPublicKey.public_bytes(),
        'signedPrekey': signedPublicPrekey.public_bytes(),
        'signature': signature
    }
    
# Step 3.1: Generate ephemeral key (a short-term key)
def generate_ephemeral_key():
    ephemeralPrivateKey = x25519.X25519PrivateKey.generate()
    ephemeralPublicKey = ephemeralPrivateKey.public_key()
    return ephemeralPrivateKey, ephemeralPublicKey

# Step 3.2: Fetch the target client's key bundle from key server
def get_target_client_key_bundle(targetClient):
    # ******* Note: CHANGE this as for now this is just a simulation, not actually fetching.*******
    targetClientIdentityPublicKey = x25519.X25519PublicKey.from_public_bytes(...)
    targetClientSignedPublicPrekey = x25519.X25519PublicKey.from_public_bytes(...)
    return targetClientIdentityPublicKey, targetClientSignedPublicPrekey

# Step 3.3: Perform triple DH
def do_triple_dh(identityPrivateKey, ephemeralPrivateKey,
                 targetClientSignedPublicPrekey, targetClientIdentityPublicKey):
    dh1 = identityPrivateKey.exchange(targetClientSignedPublicPrekey)
    dh2 = ephemeralPrivateKey.exchange(targetClientIdentityPublicKey)
    dh3 = ephemeralPrivateKey.exchange(targetClientSignedPublicPrekey)
    return dh1, dh2, dh3
    
# Step 3.4: Get shared secret
def get_shared_secret(dh1, dh2, dh3):
    return dh1 + dh2 + dh3

# Step 3.5: Derive session key (in X3DH Session Initialization; one session per 1-on-1 chat)
# Note: The session key needs to be derived for each client-to-client chat for each session.
def derive_session_key(sharedSecret, keySize=32, info=b'x3dh'):
    hkdf = HKDF(
                algorithm=hashes.SHA256(),
                length=keySize,
                salt=get_random_bytes(16),
                info=info
            )
    sessionKey = hkdf.derive(sharedSecret)
    return sessionKey

# Step 4: Encryption/Decryption with Double Ratchet (1-on-1 chats only)
# Note: The session key used here should be rotated periodically (say, per N msgs) using HKDF with chaining
# Note: These two functions are used when the sender client first sends a msg to the room.
#       The senderKey is encrypted by its owner client for each clients in the room 
#         using their existing E2EE session (i.e. X3DH derived session key).
#       Upon receiving the sender key, the other clients decrypt it and cache it.
# Note: When a client leaves or joins, only the sender who is currently sending
#         should first generate a new sender key and redistribute it to all current clients.
#       The remaining clients should do the same step only when they send a msg to the room.
# Example: Say client A is the one to rotate its sender key first upon a client leaves/joins. 
#          Then, all future msgs sent by client A are protected from the past or new client. 
#          The remaining clients will do so later when they send a msg to the room.
def encrypt_msg_with_dr(sessionKey, plainMsg):
    aesgcm = AESGCM(sessionKey)
    nonce = os.urandom(12)
    return aesgcm.encrypt(nonce, plainMsg, None)
def decrypt_msg_with_dr(sessionKey, encryptedMsg, nonce):
    aesgcm = AESGCM(sessionKey)
    return aesgcm.decrypt(nonce, encryptedMsg, None)

# Step 5.1.1: For the sender client: generate sender key and sender signing key
def generate_senderKey_and_senderSigningKey():
    senderKey = AESGCM.generate_key(bit_length=256)
    senderSigningPrivateKey = ed25519.Ed25519PrivateKey.generate()
    return senderKey, senderSigningPrivateKey

# Step 5.1.2: For all clients: keep a local cache of sender keys of all other clients in the room.
 

# Step 5.2: Encrypt plain msg with sender key
def encrypt_msg_with_senderKey(senderKey, plainMsg):
    aesgcm = AESGCM(senderKey)
    # Nonce here is no secret, but it is needed for integrity and correctness
    # Nonce must be unique per msg
    nonce = os.urandom(12)
    return aesgcm.encrypt(nonce, plainMsg, None), nonce

# Step 5.3: Sign the signature of the encrypted msg; used by the sender client
# Note: Added nonce when signing to protect msg replay if someone reuses encryptedMsg with a new nonce.
def sign_encrypted_msg_with_senderSigning_key(senderSigningPrivateKey, nonce, encryptedMsg):
    payload = nonce + encryptedMsg
    return senderSigningPrivateKey.sign(payload)

# Step 5.4: Room chats
# The sender client sends the msg securely by these info to the receiver clients.
# The receiver clients then decrypt and verify these info to get the plain msg.
def get_combined_info_to_send(roomID, senderID, encryptedMsg, nonce, signature, msgCounter):
    # Note: msgCounter is used for better protection from replay attacks.
    return {
        'roomID': roomID,
        'senderID': senderID,
        'counter': msgCounter,
        'message': encryptedMsg, 
        'nonce': nonce,
        'signature': signature
    }

# Step 5.5: Signature verification; used by the receiver clients
def verify_signature(senderSigningPublicKey, nonce, encryptedMsg, signature):
    payload = nonce + encryptedMsg
    try:
        senderSigningPublicKey.verify(signature, payload)
        return True
    except:
        return False
