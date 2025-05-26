# dr_related.py

# This is the third step of achieving E2EE in asynchronous group messaging.
# Functions here handle msg encryption/decryption with Double Ratchet (1-on-1 chats only).

import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# -----------------------------------------------------------------------------
# Double Ratchet consists of two ratchets:
#   1. DH Ratchet: Introduces new entropy with every DH key exchange.
#                  Ensures post-compromise security.
#   2. Symmetric-key Ratchet (SK Ratchet): Evolves the key every time 
#                  a message is sent or received.
#                  Ensures forward secrecy.
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

# Step 3.1: Encrypt a message with DR
def encrypt_msg_with_dr(sendingChainKey, plainMsg, dhsPublicKey=None):
    # Derives a new chain key and msg key on each msg
    newSendingChainKey, msgKey = kdf_chain_key(sendingChainKey)
    aesgcm = AESGCM(msgKey)
    nonce = os.urandom(12)
    encryptedMsg = aesgcm.encrypt(nonce, plainMsg, None)
    # Note: If the sender client's DH keys are rotated, 
    #         need to also include the new dh public key in the msg.
    return encryptedMsg, newSendingChainKey, nonce, dhsPublicKey

# Step 3.2: Decrypt a message with DR
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

# Step 3.3: This performs the core logic of DH ratchet
# Rotates the root key, gets a new chain key seed, and split the chain key seed
#   to get a new sending chain key and receiving chain key.
# This function needs to be executed once the target client's DH public key changed.
#   When it happens, first rotates current client's dhsPrivateKey and dhsPublicKey,
#   then use current client's dhsPrivateKey and target client's dhrPublicKey 
#   to perform the DH ratchet.
def dh_ratchet_step(rootKey, dhsPrivateKey, dhrPublicKey):
    sharedSecret = dhsPrivateKey.exchange(dhrPublicKey)
    newRootKey, chainKeySeed = kdf_root_key(rootKey, sharedSecret)
    # Derives a new chain key and msg key on each msg
    sendingChainKey, receivingChainKey = kdf_split_chain_keys(chainKeySeed)
    return newRootKey, sendingChainKey, receivingChainKey
