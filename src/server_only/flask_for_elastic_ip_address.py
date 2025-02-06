# flask_for_elastic_ip_address.py

import boto3
import os
from flask import Flask, jsonify

app = Flask(__name__)

ssm = boto3.client('ssm', region_name='us-east-2')

@app.route('/get-server-ip', methods=['GET'])
def get_server_ip():
    try:
        # Fetch server's elastic ip address from Parameter Store
        parameterName = 'Giraffael2-server-ip-address'
        response = ssm.get_parameter(Name=parameterName, 
                                     WithDecryption=False)
        elasticIp = response['Parameter']['Value']
        
        # Return the Elastic IP as a JSON response
        return jsonify({"Elastic ip": elasticIp}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
