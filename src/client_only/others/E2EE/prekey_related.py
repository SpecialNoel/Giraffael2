# prekey_related.py

# This is the first step of achieving E2EE in asynchronous group messaging.
# Functions here generate keys and pre-keys bundle to be uploaded to key server.

import uuid
from datetime import datetime, timezone
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import x25519, ed25519

# -----------------------------------------------------------------------------
# Helper functions: 

# Used to generate universally unique ids for keys 
#   (to be included in pre-key bundles for key's version differentiation)
def generate_key_id(prefix):
    return f'{prefix}-{uuid.uuid4()}'
# Serialize x25519 public key
def serialize_x25519_public_key(key: x25519.X25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
# Serialize ed25519 public key
def serialize_ed25519_public_key(key: ed25519.Ed25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )

# -----------------------------------------------------------------------------
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
    return signingPrivateKey.sign(serialize_x25519_public_key(signedPublicPrekey)) # signature

# Step 1.5: Get pre-key bundle
# This bundle will be uploaded to key server for other clients to fetch during X3DH steps
def get_prekey_bundle_to_be_uploaded(clientID, identityPublicKey, signingPublicKey, 
                                     signedPublicPrekey, signatureOfSignedPrekey):
    timestamp_z = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
    # identityKey should be uploaded only once, and it needs to be authenticated
    return {
        'clientID': clientID,
        'timestamp': timestamp_z,
        'identityKey': {
            'id': generate_key_id('idk'),
            'key': serialize_x25519_public_key(identityPublicKey)
        },
        'signingKey': {
            'id': generate_key_id('signingk'),
            'key': serialize_ed25519_public_key(signingPublicKey)
        },
        'signedPrekey': {
            'id': generate_key_id('signedpk'), 
            'key': serialize_x25519_public_key(signedPublicPrekey),
            'signature': signatureOfSignedPrekey
        }
    }
