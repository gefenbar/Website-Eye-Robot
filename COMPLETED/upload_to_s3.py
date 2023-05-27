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
            delete_file(file_path)
            return f'https://{bucket_name}.s3.eu-west-1.amazonaws.com/{object_name}'
        except Exception as e:
            print(f"Error uploading file: {e}")


def delete_file(file_path):
    try:
        os.remove(file_path)
        print(f"File deleted successfully: {file_path}")
    except OSError as e:
        print(f"Error deleting file: {e}")
