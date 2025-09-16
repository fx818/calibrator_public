import boto3

from dotenv import load_dotenv
import os
load_dotenv()

import boto3
import os

def upload_file_to_s3(file_path, bucket_name, s3_key):
    """
    Uploads a file to S3, setting the correct metadata for in-browser viewing.
    """
    # Create the client without hardcoding credentials
    # Boto3 will find them from environment variables or IAM roles automatically
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        )

    # Define the metadata you want to set for the object
    extra_args = {
        'ContentType': 'application/pdf',
        'ContentDisposition': 'inline'
    }

    try:
        # Pass the extra arguments during the upload
        s3_client.upload_file(
            file_path,
            bucket_name,
            s3_key,
            ExtraArgs=extra_args
        )
        print(f"Successfully uploaded '{file_path}' with correct metadata.")
    except Exception as e:
        print(f"Error uploading file: {e}")

file_path = "../downloaded_attachments/warranty.pdf"
bucket_name = "prossima"
s3_key = "warranty.pdf"

upload_file_to_s3(file_path, bucket_name, s3_key)

# import boto3
# from botocore.config import Config
# from botocore.exceptions import ClientError

# def create_presigned_url(bucket_name, object_key, expiration=3600):
#     """
#     Generate a presigned URL to share an S3 object using Signature Version 4.
#     """
#     # Replace 'your-bucket-region' with your bucket's actual region, e.g., 'ap-south-1'
#     s3_client = boto3.client(
#         's3',
#         aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
#         aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
#         region_name='ap-south-1', # <-- IMPORTANT: SET YOUR BUCKET'S REGION HERE
#         config=Config(signature_version='s3v4')
#     )

#     try:
#         response = s3_client.generate_presigned_url(
#             'get_object',
#             Params={
#                 'Bucket': bucket_name,
#                 'Key': object_key,
#                 'ResponseContentDisposition': 'inline' # <-- ADD THIS LINE
#             },
#             ExpiresIn=expiration
#         )
#         return response
#     except ClientError as e:
#         print(f"Error creating pre-signed URL: {e}")
#         return None

# --- EXAMPLE ---
# You are in Lucknow, so your Mumbai bucket region is 'ap-south-1'
# url = create_presigned_url('my-mumbai-bucket', 'documents/report.pdf')
# print(url)
# Example usage




import boto3
from botocore.config import Config
from botocore.exceptions import ClientError


bucket_name = "prossima"
object_key = "warranty.pdf"
region = "ap-south-1"  # Replace with your bucket's region

def create_presigned_url_for_viewing(bucket_name, object_key, region=region, expiration=3600):
    """
    Generates a pre-signed URL for viewing a private S3 object in a browser.

    :param bucket_name: The name of the S3 bucket.
    :param object_key: The key (path) of the object in the bucket.
    :param region: The AWS region of the bucket (e.g., 'ap-south-1').
    :param expiration: The URL's expiration time in seconds (default: 1 hour).
    :return: The pre-signed URL, or None if an error occurred.
    """
    # Create an S3 client with the necessary configuration
    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),
        aws_secret_access_key=os.getenv("AWS_SECRET_KEY"),
        region_name=region,
        # Enforce Signature Version 4 to avoid authentication errors
        config=Config(signature_version='s3v4')
    )

    try:
        # Generate the URL
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_key,
                # This header forces the browser to display the file instead of downloading it
                'ResponseContentDisposition': 'inline'
            },
            ExpiresIn=expiration
        )
        return url
    except ClientError as e:
        print(f"An error occurred: {e}")
        return None




url = create_presigned_url_for_viewing(bucket_name, object_key, region)
print(url)