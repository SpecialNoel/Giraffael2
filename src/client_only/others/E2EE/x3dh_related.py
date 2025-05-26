# x3dh_related.py

# This is the second step of achieving E2EE in asynchronous group messaging.
# Functions here perform X3DH with one target client (for one session only).

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import x25519
from cryptography.hazmat.primitives.kdf.hkdf import HKDF

# -----------------------------------------------------------------------------
# Helper functions: 

# Serialize x25519 public key
def serialize_x25519_public_key(key: x25519.X25519PublicKey) -> bytes:
    return key.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw
    )
# Deserialize x25519 public key
def deserialize_x25519_public_key(data: bytes) -> x25519.X25519PublicKey:
    return x25519.X25519PublicKey.from_public_bytes(data)

# -----------------------------------------------------------------------------
# Step 2.1: Generate ephemeral key (a short-term key)
def generate_ephemeral_key():
    ephemeralPrivateKey = x25519.X25519PrivateKey.generate()
    ephemeralPublicKey = ephemeralPrivateKey.public_key()
    return ephemeralPrivateKey, ephemeralPublicKey

# Step 2.2: Send pre-key msg (prior to any real msg) to the target client.
def send_prekey_msg_to_target_client(targetClient, clientID, identityPublicKey,
                                     ephemeralPublicKey, targetClientID, prekeyID):
    prekeyMsg = {
        'clientID': clientID,
        'identityPublicKey': serialize_x25519_public_key(identityPublicKey),
        'ephemeralPublicKey': serialize_x25519_public_key(ephemeralPublicKey),
        'prekeyBundleRef': {
            'receiverClientID': targetClientID,
            'usedSignedPrekeyID': prekeyID
        }
    }
    # Send the msg here
    send(targetClient, prekeyMsg)
    return

# Step 2.3: Fetch the target client's key bundle from key server
def get_target_client_key_bundle(targetClient):
    # ******* Note: CHANGE this as for now this is just a simulation, not actually fetching.*******
    targetClientIdentityPublicKey = deserialize_x25519_public_key(...)
    targetClientSignedPublicPrekey = deserialize_x25519_public_key(...)
    return targetClientIdentityPublicKey, targetClientSignedPublicPrekey

# Step 2.4: Verify the signature with target client's signingPublicPrekey before
#             using target client's signedPublicPrekey just fetched from key bundle
def verify_signed_prekey_signature(signingPublicPrekey, signedPublicPrekey, signature):
    return signingPublicPrekey.verify(signature, signedPublicPrekey)

# Step 2.5: Perform triple DH
def do_triple_dh(identityPrivateKey, ephemeralPrivateKey,
                 targetClientSignedPublicPrekey, targetClientIdentityPublicKey):
    dh1 = identityPrivateKey.exchange(targetClientSignedPublicPrekey)
    dh2 = ephemeralPrivateKey.exchange(targetClientIdentityPublicKey)
    dh3 = ephemeralPrivateKey.exchange(targetClientSignedPublicPrekey)
    return dh1, dh2, dh3

# Step 2.6: Get shared secret
def get_shared_secret(dh1, dh2, dh3):
    return dh1 + dh2 + dh3 # shared secret

# Step 2.7: Derive session key (in X3DH Session Initialization; one session per 1-on-1 chat)
# Note: The session key needs to be derived for each client-to-client chat for each session.
def derive_session_key(sharedSecret, salt, keySize=32, info=b'x3dh'):
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=keySize,
        salt=salt, # Needs to include this salt in the pre-key msg sent to the receiver client
        info=info
        )
    sessionKey = hkdf.derive(sharedSecret)
    return sessionKey 
