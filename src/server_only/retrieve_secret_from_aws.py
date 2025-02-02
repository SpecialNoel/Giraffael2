# retrieve_secret_from_aws.py

import boto3
import json
import ssl
import tempfile
from botocore.exceptions import ClientError

def get_api_key():
    secret_name = "Secret-for-Giraffael-2"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secretJson = get_secret_value_response['SecretString']
    secret = json.loads(secretJson)
    apiKey = secret['openai_api_key']
    return apiKey

def get_secret():
    secret_name = "Secret-for-Giraffael-2"
    region_name = "us-east-2"

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=region_name
    )

    try:
        get_secret_value_response = client.get_secret_value(
            SecretId=secret_name
        )
    except ClientError as e:
        # For a list of exceptions thrown, see
        # https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
        raise e

    secretJson = get_secret_value_response['SecretString']
    secret = json.loads(secretJson)
    certification = secret['cert.pem']
    privateKey = secret['key.pem']
    return certification, privateKey
    
def setup_ssl_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) # TLS
    certification, privateKey = get_secret()
    
    with (tempfile.NamedTemporaryFile(delete=True) as cert_file, 
          tempfile.NamedTemporaryFile(delete=True) as key_file):
        # Write certificate and key to the temporary files
        cert_file.write(certification.encode())
        cert_file.flush()
        key_file.write(privateKey.encode())
        key_file.flush()

        # Create an SSL context
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile=cert_file.name, keyfile=key_file.name)
    
    print('SSL context on server side loaded successfully!')
    return context
