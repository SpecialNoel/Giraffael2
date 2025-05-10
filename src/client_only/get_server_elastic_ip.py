# get_server_elastic_ip.py

import requests
import json

def get_server_elastic_ip():
    api_url = 'https://97f70rzwfa.execute-api.us-east-2.amazonaws.com/Giraffael2-REST-API-Stage'

    def fetch_backend_ip():
        try:
            response = requests.get(api_url)
            response.raise_for_status()
            outerResponse = response.json()
            body = outerResponse.get('body')  # Get the 'body' string
            if body:
                bodyContent = json.loads(body) # Parse the 'body' string into a dictionary
                elasticIp = bodyContent.get('ElasticIp')
                print(f'Server Elastic IP Address: {elasticIp}')
                return elasticIp
            else:
                print('Body not found in the response.')
                return None
        except Exception as e:
            print(f'Failed to fetch backend IP: {e}')
            return None

    # Fetch the backend IP
    elasticIp = fetch_backend_ip()
    return elasticIp
