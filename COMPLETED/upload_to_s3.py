import boto3
import os


class S3Uploader:
    def __init__(self, aws_access_key_id, aws_secret_access_key):
        self.session = boto3.Session(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        )

    def upload_to_s3(self, file_path, bucket_name, object_name):
        s3_client = self.session.client('s3')
        try:
            s3_client.upload_file(file_path, bucket_name, object_name)
            return f's3://{bucket_name}/{object_name}'
            os.remove(file_path)
        except Exception as e:
            print(f"Error uploading file: {e}")

# os.environ["AWS_SERVER_SECRET_KEY"]
