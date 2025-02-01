# retrieve_secret_from_aws.py

import boto3
import ssl
from botocore.exceptions import ClientError
from io import BytesIO

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

    secret = get_secret_value_response['SecretString']
    certification = secret['cert.pem']
    privateKey = secret['key.pem']
    return certification, privateKey
    
def setup_ssl_context():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER) # TLS
    certification, privateKey = get_secret()
    context.load_cert_chain(certfile=BytesIO(certification.encode()), 
                            keyfile=BytesIO(privateKey.encode()))
    print('SSL context on server side loaded successfully!')
    return context
