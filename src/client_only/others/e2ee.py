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

import os
import uuid
from datetime import datetime, timezone
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Crypto.Random import get_random_bytes

# -----------------------------------------------------------------------------
# Helper functions: 

# Used to generate universally unique ids for keys 
#   (to be included in pre-key bundles for key's version differentiation)
def generate_key_id(prefix):
    return f'{prefix}-{uuid.uuid4()}'

# -----------------------------------------------------------------------------
# Step 1: Generate keys and pre-keys

# Step 1.1: Identity key
def generate_identity_key():
    # x25519 specifies the ECDH protocol, that uses the Curve25519 elliptic curve 
    #   to securely establish a shared secret between two parties
    identityPrivateKey = x25519.X25519PrivateKey.generate()
    identityPublicKey = identityPrivateKey.public_key()
    return identityPrivateKey, identityPublicKey

# Step 1.2: Signing key
def generate_signing_key():
    signingPrivateKey = ed25519.Ed25519PrivateKey.generate()
    signingPublicKey = signingPrivateKey.public_key()
    return signingPrivateKey, signingPublicKey

# Step 1.3: Signed pre-key
def generate_signed_prekey():
    signedPrivatePrekey = x25519.X25519PrivateKey.generate()
    signedPublicPrekey = signedPrivatePrekey.public_key()
    return signedPrivatePrekey, signedPublicPrekey

# Step 1.4: Get signature of signed public pre-key
def get_signature_of_signed_prekey(signingPrivateKey, signedPublicPrekey):
    return signingPrivateKey.sign(signedPublicPrekey.public_bytes())

# -----------------------------------------------------------------------------
# Step 2: Get pre-key bundle 

# This bundle will be uploaded to key server for other clients to fetch during X3DH steps
def get_prekey_bundle_to_be_uploaded(clientID, identityPublicKey, signingPublicKey, 
                                     signedPublicPrekey, signatureOfSignedPrekey):
    timestamp_z = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    return {
        'clientID': clientID,
        'timestamp': timestamp_z,
        'identityKey': {
            'id': generate_key_id('idk'),
            'key': identityPublicKey.public_bytes()
        },
        'signingKey': {
            'id': generate_key_id('signingk'),
            'key': signingPublicKey.public_bytes()
        },
        'signedPrekey': {
            'id': generate_key_id('signedpk'), 
            'key': signedPublicPrekey.public_bytes(),
            'signature': signatureOfSignedPrekey
        }
    }
    
# -----------------------------------------------------------------------------
# Step 3: Performing X3DH with one target client (for one session only)

# Step 3.1: Generate ephemeral key (a short-term key)
def generate_ephemeral_key():
    ephemeralPrivateKey = x25519.X25519PrivateKey.generate()
    ephemeralPublicKey = ephemeralPrivateKey.public_key()
    return ephemeralPrivateKey, ephemeralPublicKey

# Step 3.2: Send pre-key msg (prior to any real msg) to the target client.
def send_prekey_msg_to_target_client(targetClient, clientID, identityPublicKey,
                                     ephemeralPublicKey, targetClientID, prekeyID):
    prekeyMsg = {
        'clientID': clientID,
        'identityPublicKey': identityPublicKey.public_bytes(),
        'ephemeralPublicKey': ephemeralPublicKey.public_bytes(),
        'prekeyBundleRef': {
            'receiverClientID': targetClientID,
            'usedSignedPrekeyID': prekeyID
        }
    }
    # Send the msg here
    send(targetClient, prekeyMsg)
    return

# Step 3.3: Fetch the target client's key bundle from key server
def get_target_client_key_bundle(targetClient):
    # ******* Note: CHANGE this as for now this is just a simulation, not actually fetching.*******
    targetClientIdentityPublicKey = x25519.X25519PublicKey.from_public_bytes(...)
    targetClientSignedPublicPrekey = x25519.X25519PublicKey.from_public_bytes(...)
    return targetClientIdentityPublicKey, targetClientSignedPublicPrekey

# Step 3.4: Perform triple DH
def do_triple_dh(identityPrivateKey, ephemeralPrivateKey,
                 targetClientSignedPublicPrekey, targetClientIdentityPublicKey):
    dh1 = identityPrivateKey.exchange(targetClientSignedPublicPrekey)
    dh2 = ephemeralPrivateKey.exchange(targetClientIdentityPublicKey)
    dh3 = ephemeralPrivateKey.exchange(targetClientSignedPublicPrekey)
    return dh1, dh2, dh3

# Step 3.5: Get shared secret
def get_shared_secret(dh1, dh2, dh3):
    return dh1 + dh2 + dh3

# Step 3.6: Derive session key (in X3DH Session Initialization; one session per 1-on-1 chat)
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

# -----------------------------------------------------------------------------
# Step 4: Encryption/Decryption with Double Ratchet (1-on-1 chats only)

# Double Ratchet consists of two ratchets:
#   1. DH Ratchet: Introduces new entropy with every DH key exchange.
#                  Ensures post-compromise security.
#   2. Symmetric-key Ratchet (SK Ratchet): Evolves the key every time 
#                  a message is sent or received.
#                  Ensutes forward secrecy.
# This means that to implement DR, each client needs to keep:
#   1. 'rootKey': shared between both parties (i.e. initialized with session key derived in X3DH)
#   2. New DH key pairs: rotates dhs keys periodically
#      a. 'dhsPrivateKey': the sender client's current DH private key
#      b. 'dhsPublicKey':  the sender client's current DH public key
#      d. 'dhrPublicKey':  the receiver client's most recently received DH public key
#   3. Symmetric ratchet chains:
#      a. 'sendingChainKey':   for msgs to be sent by this client
#      b. 'receivingChainKey': for msgs to be received by this client

# Helper functions:
# Used for implementing the DH ratchet
# Derives a new root key and new chain key seed from the shared secret
#   (i.e. rotates the root key and the chain key seed)
def kdf_root_key(rootKey, sharedSecret):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=64,    # 32 bytes for newRootKey, 32 for chainKeyseed
        salt=rootKey, # rootKey as salt
        info=b'kdfRootKeyEvolution'
    )
    output = hkdf.derive(sharedSecret)
    newRootKey = output[:32]   # Used as salt for the next rotation
    chainKeySeed = output[32:] # Used to derive new sending and receiving chain keys
    return newRootKey, chainKeySeed
# Used for implementing the symmetric-key ratchet
# Advances the sending/receiving chain every time the sender client sends/receives a msg
def kdf_chain_key(chainKey):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=64,
        salt=None,
        info=b'kdfChainKeyAdvance'
    )
    output = hkdf.derive(chainKey)
    newChainKey = output[:32] # new sending/receiving chain key to be used for next msg
    msgKey = output[32:]      # msg key used for encrypting/decrypting current msg
    return newChainKey, msgKey
# Separates sending chain key and receiving chain key from a chain key seed
def kdf_split_chain_keys(chainKeySeed):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=64,
        salt=None,
        info=b'chainKeySplit'
    )
    output = hkdf.derive(chainKeySeed)
    return output[:32], output[32:] # sendingChainKey, receivingChainKey
# Used by the sender client to rotate its dhs keys if the target client's dhr public key changed
# This needs to be executed once before doing dh_ratchet_step()
def rotate_dhs_keys():
    newDhsPrivateKey = x25519.X25519PrivateKey.generate()
    newDhsPublicKey = newDhsPrivateKey.public_key()
    return newDhsPrivateKey, newDhsPublicKey

# Step 4.1: Encrypt a message with DR
def encrypt_msg_with_dr(sendingChainKey, plainMsg, dhsPublicKey=None):
    # Derives a new chain key and msg key on each msg
    newSendingChainKey, msgKey = kdf_chain_key(sendingChainKey)
    aesgcm = AESGCM(msgKey)
    nonce = os.urandom(12)
    encryptedMsg = aesgcm.encrypt(nonce, plainMsg, None)
    # Note: If the sender client's DH keys are rotated, 
    #         need to also include the new dh public key in the msg.
    return encryptedMsg, newSendingChainKey, nonce, dhsPublicKey

# Step 4.2: Decrypt a message with DR
# Note: Before executing this function as a receiver client, 
#         always need to check if the sender client's DH public key is new.
#       If yes, then do a DH ratchet step: generates a new DH key pair 
#         for this receiver client, compute a new root key and receiving chain key, 
#         and reset the sending chain.
def decrypt_msg_with_dr(receivingChainKey, encryptedMsg, nonce):
    # Derives a new chain key and msg key on each msg
    newReceivingChainKey, msgKey = kdf_chain_key(receivingChainKey)
    aesgcm = AESGCM(msgKey)
    plainMsg = aesgcm.decrypt(nonce, encryptedMsg, None)
    # Note: Need to update this client's receivingChainKey with newSendingChainKey 
    #         for next incoming msg.
    return plainMsg, newReceivingChainKey

# Step 4.3: This performs the core logic of DH ratchet
# Rotates the root key, gets a new chain key seed, and split the chain key seed
#   to get a new sending chain key and receiving chain key.
# This function needs to be executed once the target clinet's DH public key changed
#   When it happens, first rotates current client's dhsPrivateKey and dhsPublicKey,
#   then use current client's dhsPrivateKey and target client's dhrPublicKey 
#   to perform the DH ratchet.
def dh_ratchet_step(rootKey, dhsPrivateKey, dhrPublicKey):
    sharedSecret = dhsPrivateKey.exchange(dhrPublicKey)
    newRootKey, chainKeySeed = kdf_root_key(rootKey, sharedSecret)
    # Derives a new chain key and msg key on each msg
    sendingChainKey, receivingChainKey = kdf_split_chain_keys(chainKeySeed)
    return newRootKey, sendingChainKey, receivingChainKey

# -----------------------------------------------------------------------------
# Step 5: Room chats

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

# Step 5.1: For the sender client: generate sender key and sender signing key
# senderSigningPublicKey of the sender client should be shared to all other clients:
#   1. On the first msg sent by this sender client,
#   2. When the senderKey is rotated.
def generate_senderKey_and_senderSigningKey():
    senderKey = AESGCM.generate_key(bit_length=256)
    senderSigningPrivateKey = ed25519.Ed25519PrivateKey.generate()
    senderSigningPublicKey = senderSigningPrivateKey.public_key()
    return senderKey, senderSigningPrivateKey, senderSigningPublicKey

# Note: Step 5.2 needs to be executed only once per session, or on key rotation
# Step 5.2.1: Sender client encrypts its own sender key for each of the receiving clients in the room.
def encrypt_senderKey_for_each_recipient(senderKey, sessionKeysWithRecipients):
    encryptedSenderKeys = {}
    for recipientID, sessionKey in sessionKeysWithRecipients.items():
        aesgcm = AESGCM(sessionKey)
        nonce = os.urandom(12)
        encryptedSenderKey = aesgcm.encrypt(nonce, senderKey, None)
        encryptedSenderKeys[recipientID] = {
            'encryptedSenderKey': encryptedSenderKey, 
            'nonce': nonce
        }
    return encryptedSenderKeys
# Step 5.2.2: Sender client sends the encryptedSenderKey to all other clinets in the room
def get_combined_info_for_senderKey_to_send(roomID, senderID, encryptedSenderKey, nonce, senderSigningPublicKey):
    return {
        'roomID': roomID,
        'senderID': senderID,
        'encryptedSenderKey': encryptedSenderKey,
        'nonce': nonce,
        'senderSigningPublicKey': senderSigningPublicKey.public_bytes()
        
    }
# Step 5.2.3: Receiver clients decrypt encryptedSenderKey received from sender clinet
def decrypt_senderKey(encryptedSenderKey, nonce, sessionKey):
    aesgcm = AESGCM(sessionKey)
    return aesgcm.decrypt(nonce, encryptedSenderKey, None)
# Step 5.2.4: Receiver clients deserialize senderSigningPublicKey (currently in public bytes form) received from sender client
def deserialize_senderSigningPublicKey(senderSigningPublicKeyBytes):
    return ed25519.Ed25519PublicKey.from_public_bytes(senderSigningPublicKeyBytes)

# Step 5.3: Encrypt plain msg with sender key
def encrypt_msg_with_senderKey(senderKey, plainMsg):
    aesgcm = AESGCM(senderKey)
    # Nonce here is no secret, but it is needed for integrity and correctness
    # Nonce must be unique per msg
    nonce = os.urandom(12)
    return aesgcm.encrypt(nonce, plainMsg, None), nonce

# Step 5.4: Sign the signature of the encrypted msg; used by the sender client
# Note: Added nonce when signing to protect msg replay if someone reuses encryptedMsg with a new nonce.
def sign_encrypted_msg_with_senderSigning_key(senderSigningPrivateKey, nonce, encryptedMsg):
    payload = nonce + encryptedMsg
    return senderSigningPrivateKey.sign(payload)

# Step 5.5: Sender client sends these info to all other client in the room
def get_combined_info_for_msg_to_send(roomID, senderID, encryptedMsg, nonce, signature, msgCounter):
    # Note: msgCounter is used for better protection from replay attacks.
    return {
        'roomID': roomID,
        'senderID': senderID,
        'counter': msgCounter,
        'message': encryptedMsg, 
        'nonce': nonce,
        'signature': signature
    }

# Step 5.6: For all clients: need to keep a local cache of sender keys of all other clients in the room.
# Need to cache the sender key to senderKeyCache once a client receives it from another client.
def cache_senderKey(roomID, senderID, senderKey, senderSigningPublicKey, senderKeyCache):
    if roomID not in senderKeyCache:
        senderKeyCache[roomID] = {}
    
    senderKeyCache[roomID][senderID] = {
        'senderKey': senderKey,
        'senderSigningKey': senderSigningPublicKey,
        'counter': 0
    }
    return senderKeyCache

# Step 5.7: Fetch the sender client's sender key from senderKeyCache when the receiver client wants
#               to decrypt the msg sent by that sender client.
def get_cached_sender_key(roomID, senderID, senderKeyCache):
    return senderKeyCache.get(roomID, {}).get(senderID, None)

# Step 5.8: Signature verification; used by the receiver clients
def verify_signature(senderSigningPublicKey, nonce, encryptedMsg, signature):
    payload = nonce + encryptedMsg
    try:
        senderSigningPublicKey.verify(signature, payload)
        return True
    except:
        return False

# Step 5.9: Decrypt encrypted msg with cached sender key
def decrypt_msg_with_cached_senderKey(roomID, senderID, msgCounter, encryptedMsg, 
                                      nonce, signature, senderKeyCache):
    entry = get_cached_sender_key(roomID, senderID, senderKeyCache)
    if entry:
        # Replay attack protection
        if msgCounter <= entry['counter']:
            raise Exception('Replay attack detected in decrypt_msg_with_cached_senderKey()')
        entry['counter'] = msgCounter
        
        # Verify signature
        if not verify_signature(entry['senderSigningKey'], nonce, encryptedMsg, signature):
            raise Exception('Invalid signature detected in decrypt_msg_with_cached_senderKey()')
        
        # Decrypt for plain msg
        return decrypt_msg_with_cached_senderKey(entry['senderKey'], encryptedMsg, nonce)
