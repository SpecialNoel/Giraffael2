# get_server_elastic_ip.py

import boto3

def get_server_elastic_ip():
    ssm = boto3.client('ssm', region_name='us-east-2')

    response = ssm.get_parameter(Name='Giraffael2-server-ip-address')
    elasticIp = response['Parameter']['Value']

    print('Elastic Ip:', elasticIp)
    return elasticIp
