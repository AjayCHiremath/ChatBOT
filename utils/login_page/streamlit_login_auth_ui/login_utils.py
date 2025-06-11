import re
import os
import uuid
import secrets
from argon2 import PasswordHasher
import requests
import smtplib
from email.mime.text import MIMEText
import streamlit as st

from utils.aws_utils import read_auth_file_from_s3, write_auth_file_to_s3
from utils.global_variables import OBJECT_KEYS_AUTHETICATION, APP_LINK
from utils.logger.EventLogger import log_message
ph = PasswordHasher() 

#-------{Authenticates the username and password.}--------
def check_usr_pass(username: str, password: str) -> bool:
    authorized_user_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), object_key=OBJECT_KEYS_AUTHETICATION)

    for registered_user in authorized_user_data:
        if registered_user['username'] == username or registered_user['email'] == username:
            try:
                passwd_verification_bool = ph.verify(registered_user['password'], password)
                if passwd_verification_bool == True:
                    if registered_user.get('email_verified', False):
                        st.toast("✅ Your email has been successfully verified! Please log in now.")
                        st.session_state['email_verification_checked'] = True
                        st.query_params.clear()
                        return True
                    else:
                        st.toast("❌ Please verify your email address. Check your inbox and spam folder for the confirmation link.")
                        st.session_state['email_verification_checked'] = True
                        return False
            except:
                pass
    return False


#-------{Fetches the lottie animation using the URL.}--------
def load_lottieurl(url: str) -> str:
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        pass


#-------{Checks if the user entered a valid name while creating the account.}--------
def check_valid_name(name_sign_up: str) -> bool:
    name_regex = (r'^[A-Za-z_][A-Za-z0-9_]*')

    if re.search(name_regex, name_sign_up):
        return True
    return False


#-------{Checks if the user entered a valid email while creating the account.}--------
def check_valid_email(email_sign_up: str) -> bool:
    regex = re.compile(r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+')

    if re.fullmatch(regex, email_sign_up):
        return True
    return False


#------{Verify email registration}------
def verify_email(token: str) -> bool:
    authorized_users_data = read_auth_file_from_s3(
        bucket_name=os.getenv("MY_S3_BUCKET"),
        object_key=OBJECT_KEYS_AUTHETICATION
    )
    user_found = False

    for user in authorized_users_data:
        if user.get('verification_token') == token:
            user['email_verified'] = True
            user['verification_token'] = None
            user_found = True
            break

    if user_found:
        write_auth_file_to_s3(
            authorized_user_data=authorized_users_data,
            bucket_name=os.getenv("MY_S3_BUCKET"),
            object_key=OBJECT_KEYS_AUTHETICATION
        )
        return True
    return False


#-------{Checks if the email already exists (since email needs to be unique).}--------
def check_unique_email(email_sign_up: str) -> bool:
    authorized_user_data_master = list()
    authorized_users_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), 
                        object_key=OBJECT_KEYS_AUTHETICATION)

    for user in authorized_users_data:
        authorized_user_data_master.append(user['email'])

    if email_sign_up in authorized_user_data_master:
        return False
    return True


#-------{Checks for non-empty strings.}--------
def non_empty_str_check(username_sign_up: str) -> bool:
    empty_count = 0
    for i in username_sign_up:
        if i == ' ':
            empty_count = empty_count + 1
            if empty_count == len(username_sign_up):
                return False

    if not username_sign_up:
        return False
    return True


#-------{Checks if the username already exists (since username needs to be unique), also checks for non - empty username.}--------
def check_unique_usr(username_sign_up: str):
    authorized_user_data_master = list()
    authorized_users_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), 
                        object_key=OBJECT_KEYS_AUTHETICATION)

    for user in authorized_users_data:
        authorized_user_data_master.append(user['username'])

    if username_sign_up in authorized_user_data_master:
        return False
    
    non_empty_check = non_empty_str_check(username_sign_up)

    if non_empty_check == False:
        return None
    return True


#-------{Verifies user's email id}--------
def send_verification_email(company:str, username: str, email: str, verification_token: str) -> None:
    sender_email = os.getenv("SMTP_SENDER_EMAIL")
    sender_password = os.getenv("SMTP_APP_PASSWORD")

    verification_link = f"{APP_LINK}verify?token={verification_token}"
    
    subject = f"{company}:Verify Your Email Address"
    body = (
        f"Hi {username},\n\n"
        "Thanks for signing up! Please verify your email address by clicking the link below:\n\n"
        f"{verification_link}\n\n"
        "If you did not sign up, please ignore this email.\n\n"
        "Regards,\n"
        "CHATBOT APP"
    )

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = email

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [email], msg.as_string())
        log_message(f"✔️ Verification email sent to {email}", log_file="logs/chatbot/login/", echo=True)
        st.toast(f"✔️ Verification email sent to {email}")
        st.info(f"✔️ Verification email sent to {email}")
    except Exception as e:
        log_message(f"❌ Failed to send verification email: {e}", log_file="logs/chatbot/login/", echo=True)
        st.toast(f"❌ Unexpected Error notified to development team. Please try to create account after 24 hours.")

#-------{Saves the information of the new user in the _secret_auth.json file.}--------
def register_new_usr(company:str, name_sign_up: str, email_sign_up: str, username_sign_up: str, password_sign_up: str) -> None:
    verification_token = str(uuid.uuid4())
    new_usr_data = {
        'username': username_sign_up,
        'name': name_sign_up,
        'email': email_sign_up,
        'password': ph.hash(password_sign_up),
        'email_verified': False,
        'verification_token': verification_token
    }
    # ----{ Fetch the user database from S3 }----
    authorized_user_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), 
                        object_key=OBJECT_KEYS_AUTHETICATION)

    # ----{ Append new user data }----
    authorized_user_data.append(new_usr_data)

    # ----{ Save the updated user database back to S3 }----
    write_auth_file_to_s3(authorized_user_data=authorized_user_data, 
                              bucket_name=os.getenv("MY_S3_BUCKET"), 
                              object_key=OBJECT_KEYS_AUTHETICATION)

    send_verification_email(company=company, username=username_sign_up, email=email_sign_up, verification_token=verification_token)

#-------{Checks if the username exists in the _secret_auth.json file.}--------
def check_username_exists(user_name: str) -> bool:
    authorized_user_data_master = list()
    authorized_users_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), 
                        object_key=OBJECT_KEYS_AUTHETICATION)

    for user in authorized_users_data:
        authorized_user_data_master.append(user['username'])
        
    if user_name in authorized_user_data_master:
        return True
    return False
        

#-------{Checks if the email entered is present in the _secret_auth.json file.}--------
def check_email_exists(email_forgot_passwd: str):
    authorized_users_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), 
                        object_key=OBJECT_KEYS_AUTHETICATION)

    for user in authorized_users_data:
        if user['email'] == email_forgot_passwd:
                return True, user['username']
    return False, None


#-------{Generates a random password to be sent in email.}--------
def generate_random_passwd() -> str:
    password_length = 10
    return secrets.token_urlsafe(password_length)


#-------{Triggers an email to the user containing the randomly generated password.}--------
def send_passwd_in_email(username_forgot_passwd: str, email_forgot_passwd: str, company_name: str, random_password: str) -> None:
    authorized_users_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), 
                        object_key=OBJECT_KEYS_AUTHETICATION)
    email_exists = any(user['email'] == email_forgot_passwd for user in authorized_users_data)

    if not email_exists:
        print(f"Attempted reset for non-existent email: {email_forgot_passwd}")

    sender_email = os.getenv("SMTP_SENDER_EMAIL")
    sender_password = os.getenv("SMTP_APP_PASSWORD")

    subject = f"{company_name}: Login Password!"
    body = (
        f"Hi {username_forgot_passwd},\n\n"
        f"Your temporary login password is: {random_password}\n\n"
        "Please reset your password at the earliest for security reasons."
    )

    try:
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_email
        msg['To'] = email_forgot_passwd

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, [email_forgot_passwd], msg.as_string())

        log_message(f"✔️ Password email sent to {email_forgot_passwd}", log_file="logs/chatbot/login/", echo=True)
        return True

    except Exception as e:
        log_message(f"❌ Failed to send password reset email to {email_forgot_passwd}: {e}", log_file="logs/chatbot/login/", echo=True)
        return False


#-------{Replaces the old password with the newly generated password.}--------
def change_passwd(email_: str, random_password: str) -> None:
    # ----{ Fetch the user database from S3 }----
    authorized_users_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), 
                        object_key=OBJECT_KEYS_AUTHETICATION)

    # ----{ Update the password }----
    for user in authorized_users_data:
        if user['email'] == email_:
            user['password'] = ph.hash(random_password)

    # ----{ Save the updated user database back to S3 }----
    write_auth_file_to_s3(authorized_user_data=authorized_users_data, 
                              bucket_name=os.getenv("MY_S3_BUCKET"), 
                              object_key=OBJECT_KEYS_AUTHETICATION)

#-------{Authenticates the password entered against the username when resetting the password.}--------
def check_current_passwd(email_reset_passwd: str, current_passwd: str) -> bool:
    authorized_users_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), 
                        object_key=OBJECT_KEYS_AUTHETICATION)

    for user in authorized_users_data:
        if user['email'] == email_reset_passwd:
            try:
                if ph.verify(user['password'], current_passwd) == True:
                    return True
            except:
                pass
    return False