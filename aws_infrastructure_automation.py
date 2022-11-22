import boto3
import os
from botocore.client import ClientError

USERDATA_SCRIPT = '''#!/bin/bash
cd /home/ubuntu/
git clone https://github.com/danilaSADev/AWS-Lab---Deploy-automatization.git "./cloned-dist/"
cd cloned-dist
sudo apt update
sudo apt install python3-pip --assume-yes
sudo apt install jupyter-notebook --assume-yes
pip3 install -r requirements.txt
pip3 install jupyter-notebook
pip3 install pycairo'''


def create_key_pair():
    ec2_client = boto3.client("ec2", region_name='us-east-1')
    key_pair = ec2_client.create_key_pair(KeyName="lab4-key-pair")
    private_key = key_pair["KeyMaterial"]
    with os.fdopen(os.open("lab4_ec2_key.pem", os.O_WRONLY | os.O_CREAT, 0o400), "w+") as handle:
        handle.write(private_key)


def create_instance(instance_name):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    instances = ec2_client.run_instances(
        ImageId="ami-08c40ec9ead489470",
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[
            "sg-05ab746d1e2ef73af"
        ],
        Monitoring={
            'Enabled': False
        },
        UserData = USERDATA_SCRIPT,
        InstanceType="t2.micro",
        KeyName="lab4-key-pair"
    )
    return instances["Instances"][0]


def check_if_bucket_exist(bucket_name, region=None):
    s3 = boto3.resource("s3", region_name=region)
    try:
        s3.meta.client.head_bucket(Bucket=bucket_name)
        return True
    except ClientError:
        return False


def create_s3_bucket(bucket_name, region):

    if check_if_bucket_exist(bucket_name, region):
        print("Bucket with this name already exist!")
        return

    s3 = boto3.client('s3', region_name=region)
    location = {'LocationConstraint':region}

    response = s3.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration=location
    )
    return response


def send_file_to_bucket(bucket_name, file_name, object_name):
    s3 = boto3.client('s3')
    with open(file_name, "rb") as f:
        s3.upload_file(f, bucket_name, object_name)


def output_running_instances():
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    reservations = ec2_client.describe_instances(Filters=[
        {
            "Name": "instance-state-name",
            "Values": ["running"],
        },
        {
            "Name": "instance-type",
            "Values": ["t2.micro"]
        }
    ]).get("Reservations")
    for reservation in reservations:
        for instance in reservation["Instances"]:
            instance_id = instance["InstanceId"]
            instance_type = instance["InstanceType"]
            public_ip = instance["PublicIpAddress"]
            private_ip = instance["PrivateIpAddress"]
            print(f"{instance_id}, {instance_type}, {public_ip}, {private_ip}")


def get_public_ip(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")

    reservations = ec2_client.describe_instances(InstanceIds=[instance_id]).get("Reservations")

    for reservation in reservations:
        for instance in reservation['Instances']:
            print(instance.get("PublicIpAddress"))
            return instance.get("PublicIpAddress")


def stop_instance(instance_id):
    ec2_client = boto3.client("ec2", region_name="us-east-1")
    response = ec2_client.stop_instances(InstanceIds=[instance_id])
    return response


def destroy_bucket(bucket_name, region):
    if not check_if_bucket_exist(bucket_name,region):
        print("Bucket with this name does not exist!")
        return
    s3_client = boto3.client('s3', region_name=region)
    response = s3_client.delete_bucket(Bucket=bucket_name)
    return response
