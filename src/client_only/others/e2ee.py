# e2ee.py

# This file achieves client-to-client Encryption (E2EE) with:
#   1. ECDH    (provides asymmetric key exchange of the shared key), and
#   2. AES-256 (provides symmetric encryption of data using the shared key)

# E2EE encrypts data so only the intended recipient can decrypt it 
#   (i.e. sending straight from sender to receiver, meaning that 
#   not even the server would be able to decrypt)

# Only the Client side should add the encryption and decryption methods, 
#   since the Server side should only be transmitting whatever sent from 
#   the Client side to the room (only relays the message and nothing else)
# Communication between Client and Server was protected by TLS (implemented)

# Note: Must generate a new private key (and thus public key, shared key, etc.)
#   for EACH handshake/session to ensure Perfect Forward Secrecy

# Process: 
#   1. Both parties generate ECDH key pairs (public and private keys)
#   2. Both parties serialize their own public key
#   3. Both parties send their serialized public key to each other
#   4. Both parties deserialize received public key
#   5. Both parties compute the shared secret using the deserialized public key
#   6. Both parties use the shared secret and HKDF to compute AES key and IV
#   7. The sender party uses AES key and IV to encrypt data, then send it
#   8. The receiver party uses AES key and IV to decrypt data

from client_only.others.ecdh import (generate_ecdh_keypair, 
                                     serialize_ecdh_public_key,
                                     deserialize_ecdh_public_key, 
                                     generate_ecdh_shared_secret, 
                                     derive_aes_key_and_iv)
from client_only.others.aes import (encrypt_data_with_aes_gcm, 
                                    decrypt_data_with_aes_gcm)

# Step 1: Generate ECDH key pairs (public and private keys)
def get_ecdh_keypair():
    return generate_ecdh_keypair()

# Step 2: Serialize their own public key
def get_serialized_ecdh_public_key(publicKey):
    return serialize_ecdh_public_key(publicKey)

# Step 3: Send serialized public key to another party
def send_serialize_ecdh_public_key(serializedPublicKey):
    
    return

# Step 4: Deserialize received public key
def get_deserialize_ecdh_public_key(serializedPublicKey):
    return deserialize_ecdh_public_key(serializedPublicKey)

# Step 5: Compute the shared secret using the deserialized public key
def get_ecdh_shared_secret(privateKey, publicKey):
    return generate_ecdh_shared_secret(privateKey, publicKey)

# Step 6: Compute AES key and IV using the shared secret and HKDF
def get_aes_key_and_iv(sharedSecret):
    return derive_aes_key_and_iv(sharedSecret)

# Step 7: Sender uses AES key and IV to encrypt data, then send it
def encrypt_data_with_aes_key_and_iv(aesKey, aesIv, data):
    return;

# Step 8: Receiver uses AES key and IV to decrypt data
def decrypt_data_with_aes_key_and_iv(aesKey, aesIv, encryptedData):
    return
