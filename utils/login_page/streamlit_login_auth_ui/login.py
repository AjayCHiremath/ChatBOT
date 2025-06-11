from utils.login_page.streamlit_login_auth_ui.widgets import __login__

# ---{ Login UI Function }---
def login_ui(company_name: str) -> bool:
    # ---{ Initialize login object }---
    __login__obj = __login__(
        company_name = company_name,
        logout_button_name = 'Logout',
        hide_menu_bool = True,
        hide_footer_bool = True,
    )

    # ---{ Return login objects }---
    return __login__obj