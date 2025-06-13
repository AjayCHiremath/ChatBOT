import os
import json
import io
from datetime import datetime
import streamlit as st

from utils.aws_utils import read_auth_file_from_s3
from utils.global_variables import OBJECT_KEYS_AUTHETICATION

# -- Custom writer for updating user data back to S3 --
def write_auth_file_to_s3(updated_data, bucket_name, object_key):
    try:
        json_data = json.dumps(updated_data)
        json_bytes = io.BytesIO(json_data.encode())
        s3 = st.session_state.aws_env.client('s3')
        s3.upload_fileobj(json_bytes, bucket_name, object_key)
    except Exception as e:
        st.error(f"❌ Failed to update usage history: {e}")

#------{ Check usage history }------
def check_usage_history():
    today = datetime.today().strftime('%Y-%m-%d')
    username = st.session_state.user_name

    #---{Read current auth data}---
    auth_data = read_auth_file_from_s3(
        bucket_name=os.getenv("MY_S3_BUCKET"),
        object_key=OBJECT_KEYS_AUTHETICATION
    )

    #---{ Find user in auth data }---
    user = next((u for u in auth_data if u.get('username') == username), None)

    #---{Initialize fields if missing}---
    user.setdefault('usage_history', {})

    #---{Update today's usage}---
    user['usage_history'][today] = user['usage_history'].get(today, 0) + st.session_state.response_count
    #---{Reset for next cycle}---
    st.session_state.response_count = 0
    
    #---{Update max usage}---
    user['max_usage'] = sum(user['usage_history'].values())

    #---{ Visualize usage history }---
    st.session_state.usage_history = user['usage_history']

    #---{Save updated auth data back to S3}---
    write_auth_file_to_s3(auth_data, bucket_name=os.getenv("MY_S3_BUCKET"), object_key=OBJECT_KEYS_AUTHETICATION)