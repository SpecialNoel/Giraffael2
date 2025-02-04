# associate_elastic_ip.py

import boto3

def associate_elastic_ip(instanceId, elasticIpAllocationId, region='us-east-2'):
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
    return private_ip
