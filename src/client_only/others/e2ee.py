# e2ee.py

# This file contains steps used to implement E2EE between clients with 
#   X3DH (for identification and authentication), and Double Ratchet (for 1-on-1 only).

# E2EE encrypts data so only the intended recipient can decrypt it 
#   (i.e. sending straight from sender to receiver, meaning that 
#   not even the server would be able to decrypt)

# Only the Client side should add the encryption and decryption methods, 
#   since the Server side should only be transmitting whatever sent from 
#   the Client side to the room (only relays the message and nothing else)
# Communication between Client and Server was protected by TLS (implemented)

# Note: Database for key server should be only available for uploding and querying. 
#       Each client should only be able to upload their identity key once.
#       
# Note: In database, only public keys should be stored.

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
# Note: this is mainly used for X3DH with other clients.
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
# Note: the session key needs to be derived for each client-to-client chat for each session.
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
# Note: this function is simplified; need to replace this using a library if in production)
# Note: the session key used here should be rotated periodically (say, per N msgs) using HKDF with chaining
def encrypt_msg_with_dr(sessionKey, plainMsg):
    aesgcm = AESGCM(sessionKey)
    nonce = os.urandom(12)
    return aesgcm.encrypt(nonce, plainMsg, None)
def decrypt_msg_with_dr(sessionKey, encryptedMsg, nonce):
    aesgcm = AESGCM(sessionKey)
    return aesgcm.decrypt(nonce, encryptedMsg, None)

# Step 5.1: Generate sender key and sender signing key
def generate_senderKey_and_senderSigningKey():
    senderKey = AESGCM.generate_key(bit_length=256)
    senderSigningPrivateKey = ed25519.Ed25519PrivateKey.generate()
    return senderKey, senderSigningPrivateKey

# Step 5.2: Encrypt plain msg with sender key
def encrypt_msg_with_senderKey(senderKey, plainMsg):
    aesgcm = AESGCM(senderKey)
    # Nonce here is no secret, but it is needed for integrity and correctness
    # Nonce must be unique per msg
    nonce = os.urandom(12)
    return aesgcm.encrypt(nonce, plainMsg, None)

# Step 5.3: Sign the signature of the encrypted msg with sender signing private key
def sign_encrypted_msg_with_senderSigning_key(senderSigningPrivateKey, encryptedMsg):
    return senderSigningPrivateKey.sign(encryptedMsg)

# Step 5.4: Room chats
# The sender client sends the msg securely by these info to the receiver clients.
# The receiver clients then decrypt and verify these info to get the plain msg.
def get_combined_info_to_send(roomID, senderID, encryptedMsg, nonce, signature):
    return {
        'roomID': roomID,
        'senderID': senderID,
        'message': encryptedMsg, 
        'nonce': nonce,
        'signature': signature
    }
