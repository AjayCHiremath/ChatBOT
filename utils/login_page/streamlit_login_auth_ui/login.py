import streamlit as st
from utils.login_page.streamlit_login_auth_ui.widgets import __login__

# ---{ Login UI Function }---
def login_ui(auth_token: str, company_name: str, width: int = 200, height: int = 250) -> bool:
    # ---{ Initialize login object }---
    __login__obj = __login__(
        auth_token = auth_token,
        company_name = company_name,
        width = width,
        height = height,
        logout_button_name = 'Logout',
        hide_menu_bool = True,
        hide_footer_bool = True,
    )
    
    # ---{ Build the login UI and check login status }---
    LOGGED_IN = __login__obj.build_login_ui()
    
    # ---{ Return login status }---
    return LOGGED_IN