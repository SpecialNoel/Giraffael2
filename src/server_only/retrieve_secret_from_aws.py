# retrieve_secret_from_aws.py

import boto3
import json
import ssl
import tempfile

def get_secret():
    secret_name = 'Secret-for-Giraffael-2'
    region_name = 'us-east-2'
    client = boto3.client('secretsmanager', region_name)
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

def get_api_key():
    secret_name = 'Secret-for-Giraffael-2'
    region_name = 'us-east-2'
    client = boto3.client('secretsmanager', region_name)
    response = client.get_secret_value(SecretId=secret_name)
    print(json.loads(response['SecretString'])['openai_api_key'][:20])
    return ''

def get_cert_and_key():
    secret = get_secret()
    return secret['cert.pem'], secret['key.pem']
    
def setup_ssl_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) # TLS
    certificate, privateKey = get_cert_and_key()
    
    with (tempfile.NamedTemporaryFile(delete=True) as cert_file, 
          tempfile.NamedTemporaryFile(delete=True) as key_file):
        # Write certificate and key to the temporary files
        cert_file.write(certificate.encode())
        cert_file.flush()
        key_file.write(privateKey.encode())
        key_file.flush()

        # Create an SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_file.name, keyfile=key_file.name)
    
    print('SSL context on server side loaded successfully!')
    return context
