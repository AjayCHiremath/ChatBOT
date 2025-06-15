import json
import io
import streamlit as st
import os

#----{ Read auth file from S3 }------
def read_auth_file_from_s3(bucket_name, object_key, use_locally=False):
    try:
        if not use_locally:
            #----{ Connect to S3 client }------
            s3 = st.session_state.aws_env.client('s3')

            #----{ Download file from S3 }------
            response = s3.get_object(Bucket=bucket_name, Key=object_key)
            content = response['Body'].read().decode('utf-8')
        else:
            #----{ Ensure local file exists }------
            if not os.path.exists(object_key):
                return []

            #----{ Read from local file }------
            with open(object_key, 'r') as file:
                content = file.read()
        
        #----{ Parse and return JSON data }------
        authorized_user_data = json.loads(content)
        return authorized_user_data if isinstance(authorized_user_data, list) else [authorized_user_data]
    
    except Exception as e:
        return []

#----{ Write auth file to S3 }------
def write_auth_file_to_s3(authorized_user_data, bucket_name, object_key, use_locally=False):
    try:
        if not isinstance(authorized_user_data, list):
            authorized_user_data = []
        #----{ Serialize JSON data to memory }------
        json_data = json.dumps(authorized_user_data)

        if not use_locally:
            json_bytes = io.BytesIO(json_data.encode())
            s3 = st.session_state.aws_env.client('s3')
            s3.upload_fileobj(json_bytes, bucket_name, object_key)
        else:
            #----{ Ensure directory exists }------
            local_dir = os.path.dirname(object_key)
            if local_dir and not os.path.exists(local_dir):
                os.makedirs(local_dir, exist_ok=True)

            #----{ Write to local file }------
            with open(object_key, 'w') as file:
                file.write(json_data)

    except Exception as e:
        return