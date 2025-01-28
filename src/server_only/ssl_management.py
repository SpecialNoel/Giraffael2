# ssl_management.py

'''
openssl command to create a ssl certificate and private key:
  openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes

-x509:            Generates an X.509 certificate.
-newkey rsa:2048: Creates a new RSA key pair with a 2048-bit key.
-keyout key.pem:  Saves the private key to key.pem.
-out cert.pem:    Saves the certificate to cert.pem.
-days 365:        The certificate will be valid for 365 days.
-nodes:           No password will be set for the private key (useful for server automation).
'''

import os
import ssl

def setup_ssl_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    pathToCert = find_file_from_root_dir('cert.pem')
    pathToKey = find_file_from_root_dir('key.pem')
    context.load_cert_chain(certfile=pathToCert, keyfile=pathToKey)
    print("SSL context on server side loaded successfully!")
    return context

def find_file_from_root_dir(filename):
    current_path = os.path.dirname(os.path.abspath(__file__))
    grandparent_path = os.path.dirname(os.path.dirname(current_path))
    return os.path.join(grandparent_path, filename)
