import streamlit as st
import os
from streamlit_oauth import OAuth2Component
import secrets
import requests

from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from streamlit_cookies_manager import EncryptedCookieManager

from utils.login_page.streamlit_login_auth_ui.login_utils import verify_email
from utils.login_page.streamlit_login_auth_ui.login_utils import (check_usr_pass, load_lottieurl, check_valid_name, 
                                                            check_valid_email, check_unique_email, check_unique_usr, 
                                                            register_new_usr, check_email_exists, generate_random_passwd, 
                                                            send_passwd_in_email, change_passwd, check_current_passwd)
from utils.aws_utils import read_auth_file_from_s3, write_auth_file_to_s3
from utils.global_variables import OBJECT_KEYS_AUTHETICATION, APP_LINK

#--------{Builds the UI for the Login/ Sign Up page.}-------
class __login__:
    def __init__(self, company_name: str, logout_button_name: str = 'Logout', 
                 hide_menu_bool: bool = False, hide_footer_bool: bool = False, 
                 lottie_url: str = "https://lottie.host/d4bdd3d4-c7a7-433b-beb4-780d2c34f831/y9JJMAmfcM.json" ):
        self.company_name = company_name
        self.logout_button_name = logout_button_name
        self.hide_menu_bool = hide_menu_bool
        self.hide_footer_bool = hide_footer_bool
        self.lottie_url = lottie_url

        self.cookies = EncryptedCookieManager(
        prefix="streamlit_login_ui_yummy_cookies",
        password='9d68d6f2-4258-45c9-96eb-2d6bc74ddbb5-d8f49cab-edbb-404a-94d0-b25b1d4a564b')

        if not self.cookies.ready():
            st.stop()   


    def get_username(self):
        if st.session_state['LOGOUT_BUTTON_HIT'] == False:
            fetched_cookies = self.cookies
            if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
                username=fetched_cookies['__streamlit_login_signup_ui_username__']
                return username
 

    #--------{Creates the login widget, checks and sets cookies, authenticates the users.}-------
    def login_widget(self) -> None:
        # Checks if cookie exists (user already logged in)
        if st.session_state['LOGGED_IN'] == False:
            if st.session_state['LOGOUT_BUTTON_HIT'] == False:
                fetched_cookies = self.cookies
                if '__streamlit_login_signup_ui_username__' in fetched_cookies.keys():
                    if fetched_cookies['__streamlit_login_signup_ui_username__'] != '1c9a923f-fb21-4a91-b3f3-5f18e3f01182':
                        st.session_state['LOGGED_IN'] = True

        if st.session_state['LOGGED_IN'] == False:
            st.session_state['LOGOUT_BUTTON_HIT'] = False 

            del_login = st.empty()
            # --- Traditional Username/Password Login Form ---
            with del_login.form("Login Form"):
                st.subheader("🔐 Sign in with username and password")
                user_input = st.text_input("Username or Email", placeholder='Your unique username or email')
                password = st.text_input("Password", placeholder='Your password', type='password')
                login_submit_button = st.form_submit_button(label='Login')

                if login_submit_button:
                    authenticate_user_check = check_usr_pass(user_input, password)
                    if not authenticate_user_check:
                        st.error("❌ Invalid Username or Password!")
                    else:
                        st.session_state['LOGGED_IN'] = True
                        self.cookies['__streamlit_login_signup_ui_username__'] = user_input
                        self.cookies.save()
                        del_login.empty()
                        st.rerun()

            # --- Google OAuth Login Button ---
            st.markdown("---")
            st.subheader("🔓 Or login with Google")

            GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
            GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
            
            
            oauth2 = OAuth2Component(
                client_id=GOOGLE_CLIENT_ID,
                client_secret=GOOGLE_CLIENT_SECRET,
                authorize_endpoint="https://accounts.google.com/o/oauth2/v2/auth",
                token_endpoint="https://oauth2.googleapis.com/token",
            )
            
            result = oauth2.authorize_button(
                name="Continue with Google",
                redirect_uri=APP_LINK,
                scope="openid email profile",
                key="google_login"
            )

            # If the user is authenticated, result will contain user info
            if result:
                token = result.get("token", {})
                access_token = token.get("access_token")

                if access_token:
                    response = requests.get(
                        "https://www.googleapis.com/oauth2/v2/userinfo",
                        headers={"Authorization": f"Bearer {access_token}"}
                    )

                    if response.status_code == 200:
                        userinfo = response.json()
                        email = userinfo.get("email")
                        name = userinfo.get("name") or email.split("@")[0]

                        # Check if user exists in your AWS database
                        email_exists, registered_username = check_email_exists(email)

                        if not email_exists:
                            # Auto-generate username with a suffix to ensure uniqueness
                            base_username = email.split("@")[0]
                            random_suffix = secrets.token_hex(2)
                            new_username = f"{base_username}_{random_suffix}"

                            # Generate a secure random password
                            random_password = generate_random_passwd()

                            # Register the user in AWS via existing function
                            register_new_usr(
                                company=self.company_name,
                                name_sign_up=name,
                                email_sign_up=email,
                                username_sign_up=new_username,
                                password_sign_up=random_password,
                                is_oauth="google",
                                max_usage=0
                            )

                            # Email the user their generated password
                            send_passwd_in_email(
                                username_forgot_passwd=new_username,
                                email_forgot_passwd=email,
                                company_name=self.company_name,
                                random_password=random_password
                            )

                            registered_username = new_username
                            st.toast("✔️ Google account auto-registered! Temporary password sent to your email.")

                # Proceed with login
                st.success(f"✔️ Logged in as: {email}")
                st.session_state['LOGGED_IN'] = True
                self.cookies['__streamlit_login_signup_ui_username__'] = registered_username
                self.cookies.save()
                st.rerun()


    #--------{Renders the lottie animation.}-------
    def animation(self) -> None:
        lottie_json = load_lottieurl(self.lottie_url)
        if lottie_json: st_lottie(lottie_json, quality='high')


    #--------{Creates the sign-up widget and stores the user info in a secure way in the _secret_auth_.json file.}-------
    def sign_up_widget(self) -> None:
        with st.form("Sign Up Form"):
            name_sign_up = st.text_input("Name *", placeholder = 'Please enter your name')
            valid_name_check = check_valid_name(name_sign_up)

            email_sign_up = st.text_input("Email *", placeholder = 'Please enter your email')
            valid_email_check = check_valid_email(email_sign_up)
            unique_email_check = check_unique_email(email_sign_up)
            
            username_sign_up = st.text_input("Username *", placeholder = 'Enter a unique username')
            unique_username_check = check_unique_usr(username_sign_up)

            password_sign_up = st.text_input("Password *", placeholder = 'Create a strong password', type = 'password')

            st.markdown("###")
            sign_up_submit_button = st.form_submit_button(label = 'Register')

            if sign_up_submit_button:
                if valid_name_check == False:
                    st.error("Please enter a valid name!")

                elif valid_email_check == False:
                    st.error("Please enter a valid Email!")
                
                elif unique_email_check == False:
                    st.error("Email already exists!")
                
                elif unique_username_check == False:
                    st.error(f'Sorry, username {username_sign_up} already exists!')
                
                elif unique_username_check == None:
                    st.error('Please enter a non - empty Username!')

                if valid_name_check == True:
                    if valid_email_check == True:
                        if unique_email_check == True:
                            if unique_username_check == True:
                                register_new_usr(self.company_name, name_sign_up, email_sign_up, 
                                                 username_sign_up, password_sign_up, "not google",
                                                 max_usage=0)
                                st.success("Registration Successful! Please check your mailbox to confirm signup.")


    #--------{Creates the forgot password widget and after user authentication (email), triggers an email to the user containing a random password.}-------
    def forgot_password(self) -> None:
        with st.form("Forgot Password Form"):
            email_forgot_passwd = st.text_input("Email", placeholder= 'Please enter your email')
            email_exists_check, username_forgot_passwd = check_email_exists(email_forgot_passwd)

            st.markdown("###")
            forgot_passwd_submit_button = st.form_submit_button(label = 'Get Password')

            if forgot_passwd_submit_button:
                if email_exists_check == False:
                    st.error("Email ID not registered with us!")

                if email_exists_check == True:
                    random_password = generate_random_passwd()
                    send_passwd_in_email(username_forgot_passwd, email_forgot_passwd, self.company_name, random_password)
                    change_passwd(email_forgot_passwd, random_password)
                    st.success("Secure Password Sent Successfully!")


    #--------{Creates the reset password widget and after user authentication (email and the password shared over that email), resets the password and updates the same in the _secret_auth_.json file.}-------
    def reset_password(self) -> None:
        with st.form("Reset Password Form"):
            email_reset_passwd = st.text_input("Email", placeholder= 'Please enter your email')
            email_exists_check, username_reset_passwd = check_email_exists(email_reset_passwd)

            current_passwd = st.text_input("Temporary Password", placeholder= 'Please enter the password you received in the email')
            current_passwd_check = check_current_passwd(email_reset_passwd, current_passwd)

            new_passwd = st.text_input("New Password", placeholder= 'Please enter a new, strong password', type = 'password')

            new_passwd_1 = st.text_input("Re - Enter New Password", placeholder= 'Please re- enter the new password', type = 'password')

            st.markdown("###")
            reset_passwd_submit_button = st.form_submit_button(label = 'Reset Password')

            if reset_passwd_submit_button:
                if email_exists_check == False:
                    st.error("Email does not exist!")

                elif current_passwd_check == False:
                    st.error("Incorrect temporary password!")

                elif new_passwd != new_passwd_1:
                    st.error("Passwords don't match!")
            
                if email_exists_check == True:
                    if current_passwd_check == True:
                        change_passwd(email_reset_passwd, new_passwd)
                        st.success("Password Reset Successfully!")
                

    #--------{Creates the logout widget in the sidebar only if the user is logged in.}-------
    def logout_widget(self) -> None:
        if st.session_state['LOGGED_IN'] == True:
            del_logout = st.sidebar.empty()
            del_logout.markdown("#")
            logout_click_check = del_logout.button(self.logout_button_name)

            if logout_click_check == True:
                st.session_state['LOGOUT_BUTTON_HIT'] = True
                st.session_state['LOGGED_IN'] = False
                self.cookies['__streamlit_login_signup_ui_username__'] = '1c9a923f-fb21-4a91-b3f3-5f18e3f01182'
                del_logout.empty()
                st.rerun()
        

    #--------{Creates the side navigaton bar}-------
    def nav_sidebar(self):
        main_page_sidebar = st.sidebar.empty()
        with main_page_sidebar:
            selected_option = option_menu(
                menu_title = 'Navigation',
                menu_icon = 'list-columns-reverse',
                icons = ['box-arrow-in-right', 'person-plus', 'x-circle','arrow-counterclockwise'],
                options = ['Login', 'Create Account', 'Forgot Password?', 'Reset Password'],
                styles = {
                    "container": {"padding": "5px"},
                    "nav-link": {"font-size": "14px", "text-align": "left", "margin":"0px"}} )
        return main_page_sidebar, selected_option
    

    #--------{Hides the streamlit menu situated in the top right.}-------
    def hide_menu(self) -> None:
        st.markdown(""" <style>
        #MainMenu {visibility: hidden;}
        </style> """, unsafe_allow_html=True)

    #------{Hides the 'made with streamlit' footer.}------
    def hide_footer(self) -> None:
        st.markdown(""" <style>
        footer {visibility: hidden;}
        </style> """, unsafe_allow_html=True)

    #--------{Brings everything together, calls important functions.}-------
    def build_login_ui(self):
        if 'LOGGED_IN' not in st.session_state:
            st.session_state['LOGGED_IN'] = False

        if 'LOGOUT_BUTTON_HIT' not in st.session_state:
            st.session_state['LOGOUT_BUTTON_HIT'] = False

        parsed_url = st.query_params
        if 'email_verification_checked' not in st.session_state:
            st.session_state['email_verification_checked'] = False

        if not st.session_state['email_verification_checked']:
            token = parsed_url.get("token")
            if token and isinstance(token, str) and len(token.strip()) > 0:
                if isinstance(token, list):
                    token = token[0]
                verified = verify_email(token)
                if verified:
                    st.toast("✔️ Your email has been successfully verified! Please log in now.")

        authorized_user_data = read_auth_file_from_s3(bucket_name=os.getenv("MY_S3_BUCKET"), 
                                                    object_key=OBJECT_KEYS_AUTHETICATION,
                                                    use_locally=False)
        
        if not authorized_user_data:
            authorized_user_data = []
            write_auth_file_to_s3(authorized_user_data=authorized_user_data, 
                                bucket_name=os.getenv("MY_S3_BUCKET"), 
                                object_key=OBJECT_KEYS_AUTHETICATION,
                                use_locally=False)

        main_page_sidebar, selected_option = self.nav_sidebar()

        if selected_option == 'Login':
            c1, c2 = st.columns([7,3])
            with c1:
                self.login_widget()
            with c2:
                if st.session_state['LOGGED_IN'] == False:
                    self.animation()
        
        if selected_option == 'Create Account':
            self.sign_up_widget()

        if selected_option == 'Forgot Password?':
            self.forgot_password()

        if selected_option == 'Reset Password':
            self.reset_password()
        
        self.logout_widget()

        if st.session_state['LOGGED_IN'] == True:
            main_page_sidebar.empty()
        
        if self.hide_menu_bool == True:
            self.hide_menu()
        
        if self.hide_footer_bool == True:
            self.hide_footer()
        
        return st.session_state['LOGGED_IN']