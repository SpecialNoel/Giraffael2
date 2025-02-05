# get_server_elastic_ip.py

import boto3

def get_elastic_ip():
    ssm = boto3.client('ssm', region_name='us-east-2')
    response = ssm.get_parameter(Name='Giraffael2-server-ip-address',
                                 WithDecryption=False)
    elastic_ip = response['Parameter']['Value']
    print(f"Server IP: {elastic_ip}")
    return elastic_ip # public ip of remote server on aws ec2

'''
def get_elastic_ip(instanceId, elasticIpAllocationId, region):
    ec2 = boto3.client('ec2', region_name=region)
    
    # Get the current private/public IP of the instance
    instance_info = ec2.describe_instances(InstanceIds=[instanceId])
    instance = instance_info['Reservations'][0]['Instances'][0]

    private_ip = instance['PrivateIpAddress']
    public_ip = instance.get('PublicIpAddress', 'No Public IP assigned yet')

    print(f'Instance {instanceId} Private IP: {private_ip}')
    print(f'Instance {instanceId} Public IP: {public_ip}')

    # Associate the Elastic IP with the instance
    response = ec2.associate_address(
        InstanceId=instanceId,
        AllocationId=elasticIpAllocationId
    )

    print('Elastic IP associated successfully.')
    print('Association ID:', response['AssociationId'])
    return public_ip # public ip should be returned
'''
