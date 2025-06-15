import os
import json
import io
from datetime import datetime, timezone, timedelta
import streamlit as st
import time

from utils.aws_utils import read_auth_file_from_s3
from utils.global_variables import OBJECT_KEYS_AUTHETICATION

# -- Custom writer for updating user data back to S3 --
def write_auth_file_to_s3(updated_data, bucket_name, object_key, use_locally=False):
    try:
        json_data = json.dumps(updated_data)
        
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
        st.error(f"❌ Failed to update usage history: {e}")

def is_rate_limited(user, now, limit=5):
    #----{ Calculate one minute ago }------
    one_minute_ago = now - timedelta(minutes=1)
    user.get("request_timestamps", [])
    
    #---{ Initialize request timestamps if missing }---
    if "request_timestamps" not in user:
        user["request_timestamps"] = []

    user["request_timestamps"] = [
        ts for ts in user["request_timestamps"]
        if datetime.fromisoformat(ts) > one_minute_ago
    ]

    #---{Enforce rate limit}---
    if len(user["request_timestamps"]) >= limit:
        cooldown_until = (now + timedelta(minutes=1)).isoformat()
        st.session_state.cooldown_until = cooldown_until
        st.toast(f"⚠️ Rate limit exceeded. Please wait till {cooldown_until} to make more requests.")
        with st.sidebar:
            with st.spinner("Enforcing cooldown..."):
                st.markdown(f"⚠️ Rate limit exceeded. Please wait till {cooldown_until} to make more requests.")
                time.sleep(60)  # Sleep for 60 seconds to enforce cooldown
        st.rerun()

    #---{Record valid request}---
    user["request_timestamps"].append(now.isoformat())

#------{ Enforce rate limit (5 requests/minute) }------
def handle_cooldown(now):
    #---{ Check if cooldown is active }---
    cooldown = st.session_state.get("cooldown_until")
    if cooldown:
        #---{ If cooldown is active, check if it's still valid }---
        cooldown_time = datetime.fromisoformat(cooldown)
        if now < cooldown_time:
            st.rerun()
        else:
            #---{ Cooldown expired, remove it }---
            del st.session_state.cooldown_until

#------{ Check usage history }------
def check_usage_history():
    #---{ Get current time in UTC }---
    now = datetime.now(timezone.utc)

    #---{ Check if rate limit is active }---
    handle_cooldown(now)
    
    #---{ Reload user name if not set }---
    if st.session_state.user_name is None:
        st.rerun()

    #------{Identify user}------
    username = st.session_state.user_name
    
    #---{Read current auth data}---
    auth_data = read_auth_file_from_s3(
        bucket_name=os.getenv("MY_S3_BUCKET"),
        object_key=OBJECT_KEYS_AUTHETICATION,
        use_locally=False
    )

    #---{ Find user in auth data }---
    user = next((u for u in auth_data if u.get('username') == username), None)
    
    if user is None:
        st.rerun()

    #----{ Apply rate limit }----
    is_rate_limited(user, now, limit=5)

    #---{Initialize fields if missing}---
    user.get('usage_history', {})

    #---{ Initialize usage history if missing }---
    if 'usage_history' not in user:
        user['usage_history'] = {}

    #---{Update today's usage}---
    today = datetime.today().strftime('%Y-%m-%d')
    user['usage_history'][today] = user['usage_history'].get(today, 0) + st.session_state.response_count

    #---{Reset for next cycle}---
    st.session_state.response_count = 0
    
    #---{Update max usage}---
    user['max_usage'] = sum(user['usage_history'].values())

    #---{ Visualize usage history }---
    st.session_state.usage_history = user['usage_history']

    #---{Save updated auth data back to S3}---
    write_auth_file_to_s3(auth_data, bucket_name=os.getenv("MY_S3_BUCKET"), object_key=OBJECT_KEYS_AUTHETICATION, use_locally=False)
