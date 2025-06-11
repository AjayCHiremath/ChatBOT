import json
import io
import streamlit as st

#----{ Read auth file from S3 }------
def read_auth_file_from_s3(bucket_name, object_key):
    try:
        
        #----{ Connect to S3 client }------
        s3 = st.session_state.aws_env.client('s3')

        #----{ Download file to local }------
        response = s3.get_object(Bucket=bucket_name, Key=object_key)
        content = response['Body'].read().decode('utf-8')
        authorized_user_data = json.loads(content)

        #----{ Return data }------
        return authorized_user_data if isinstance(authorized_user_data, list) else [authorized_user_data]
    
    except Exception as e:
        return []

#----{ Write auth file to S3 }------
def write_auth_file_to_s3(authorized_user_data, bucket_name, object_key):
    try:
        if not isinstance(authorized_user_data, list):
            authorized_user_data = []
        #----{ Serialize JSON data to memory }------
        json_data = json.dumps(authorized_user_data)
        json_bytes = io.BytesIO(json_data.encode())
        
        #----{ Connect to S3 client }------
        s3 = st.session_state.aws_env.client('s3')
        
        #----{ Upload JSON directly from memory }------
        s3.upload_fileobj(json_bytes, bucket_name, object_key)
    except Exception as e:
        return