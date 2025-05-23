# retrieve_secret_from_aws.py

import boto3
import json
import ssl
import tempfile
from server_only.others.settings import serverIsLocal

def get_secret():
    secret_name = 'Secret-for-Giraffael-2'
    region_name = 'us-east-2'
    client = boto3.client('secretsmanager', region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

def get_api_key(): # OpenAI
    secret = get_secret()
    return secret['openai_api_key'] 

def get_cert_and_key(): 
    secret = get_secret()
    return secret['cert.pem'], secret['key.pem']
    
def setup_tls_context_remote():
    if serverIsLocal:
        return None
    
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) # TLS
    certificate, privateKey = get_cert_and_key()
    
    with (tempfile.NamedTemporaryFile(delete=True) as cert_file, 
          tempfile.NamedTemporaryFile(delete=True) as key_file):
        # Write certificate and key to the temporary files
        certificate = certificate.replace('-----BEGIN CERTIFICATE----- ', '-----BEGIN CERTIFICATE----- \n')
        certificate = certificate.replace('-----END CERTIFICATE-----', '\n-----END CERTIFICATE-----')
        cert_file.write(certificate.encode())
        cert_file.flush()
        
        privateKey = privateKey.replace('-----BEGIN PRIVATE KEY----- ', '-----BEGIN PRIVATE KEY----- \n')
        privateKey = privateKey.replace('-----END PRIVATE KEY-----', '\n-----END PRIVATE KEY-----')
        key_file.write(privateKey.encode())
        key_file.flush()

        # Create an TLS context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_file.name, keyfile=key_file.name)
    
    print('TLS context on server side loaded successfully!')
    return context
 