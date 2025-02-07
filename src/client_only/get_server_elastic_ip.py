# get_server_elastic_ip.py

import requests

def get_server_elastic_ip():
    response = requests.get('http://Giraffael2-Load-Balancer-1365680863.us-east-2.elb.amazonaws.com/get-server-ip')
    if response.status_code == 200:
        elasticIp = response.json()['ElasticIp']
        print(f"Elastic IP: {elasticIp}")
        return elasticIp
    else:
        print("Failed to fetch the Elastic IP:", response.json())
        return ''
