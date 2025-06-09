import boto3
from utils.logger.EventLogger import log_message
import json
import io

#----{ Read auth file from S3 }------
def read_auth_file_from_s3(bucket_name='userdatabase-generative-application-chatbot', object_key='_secret_auth_.json'):
    try:
        #----{ Connect to S3 client }------
        s3 = boto3.client('s3', region_name='us-east-1')

        #----{ Download file to local }------
        s3.download_file(bucket_name, object_key, '_secret_auth_.json')
        #----{ Read JSON data }------
        with open('_secret_auth_.json', 'r') as auth_json:
            authorized_user_data = json.load(auth_json)
        #----{ Return data }------
        return authorized_user_data
    
    except Exception as e:
        log_message(f"[Error] read_auth_file_from_s3 failed: {e}", log_file="logs/chatbot/login/")
        return []

#----{ Write auth file to S3 }------
def write_auth_file_to_s3(authorized_user_data, bucket_name='userdatabase-generative-application-chatbot', object_key='_secret_auth_.json'):
    try:
        #----{ Serialize JSON data to memory }------
        json_data = json.dumps(authorized_user_data)
        json_bytes = io.BytesIO(json_data.encode())
        #----{ Connect to S3 client }------
        s3 = boto3.client('s3')
        #----{ Upload JSON directly from memory }------
        s3.upload_fileobj(json_bytes, bucket_name, object_key)
    except Exception as e:
        log_message(f"[Error] write_auth_file_to_s3 failed: {e}", log_file="logs/chatbot/login/")