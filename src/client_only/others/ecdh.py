# ecdh.py

# This file contains methods needed to implement ECDH part of E2EE.

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from Crypto.Random import get_random_bytes

# x25519 specifies the ECDH protocol, that uses the Curve25519 elliptic curve 
#   to securely establish a shared secret between two parties
def generate_ecdh_keypair():
    privateKey = x25519.X25519PrivateKey.generate()
    publicKey = privateKey.public_key()
    return privateKey, publicKey

# Serialize the public key before sending it to another party
# Only the public key needs to be serialized, as the private key
#   should never be transmitted over any channel
def serialize_ecdh_public_key(publicKey):
    return publicKey.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
# Deserialize the public key received from another party to compute shared key 
def deserialize_ecdh_public_key(serializedPublicKey):
    return serialization.load_pem_public_key(serializedPublicKey)

# Generate a shared secret using private key and public key
# Both privateKey and publicKey should be deserialized before exchanging,
# Shared secret should be the same after being computed by both parties
def generate_ecdh_shared_secret(privateKey, publicKey):
    return privateKey.exchange(publicKey)

# Perform key derivation using SHA256 and the shared key
# AES key and IV should be the same after being computed by both parties
def derive_aes_key_and_iv(sharedSecret, keySize=32, info=b'AES Key IV Derivation'):
    ivSize = 16
    key_and_iv = HKDF(
                    algorithm=hashes.SHA256(),
                    length=keySize + ivSize, # 32 bytes for key, 16 bytes for IV
                    salt=get_random_bytes(16),
                    info=info
                ).derive(sharedSecret)
    aesKey = key_and_iv[:keySize]
    aesIv = key_and_iv[keySize:keySize+ivSize]
    return aesKey, aesIv
