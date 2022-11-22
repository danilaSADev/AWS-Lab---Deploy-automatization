import aws_infrastructure_automation as aws
#
bucket_name = 'test-lab4-bucket'
# # working with instance
instance = aws.create_instance(aws.USERDATA_SCRIPT)

# working with bucket
aws.create_s3_bucket(bucket_name, 'us-east-1')

aws.upload_file_to_bucket(bucket_name, 'requirements.txt', 'tmp/requirements.txt')
info = aws.read_from_bucket(bucket_name, 'tmp/requirements.txt')

print(info)
