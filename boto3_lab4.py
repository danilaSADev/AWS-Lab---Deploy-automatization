import boto3
from botocore.client import ClientError


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
    print(response)


def destroy_bucket(bucket_name, region):
    if not check_if_bucket_exist(bucket_name,region):
        print("Bucket with this name does not exist!")
        return
    s3_client = boto3.client('s3', region_name=region)
    response = s3_client.delete_bucket(Bucket=bucket_name)
    print(response)
