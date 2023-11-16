import streamlit as st
from auth_helpers import *

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="documentation\SlideChatter.ico"
)

if check_login():
    st.title("User Settings")
    changepw_tab, change_api_tab = st.tabs(["**Change Password**", "**Change OPENAI API KEY**"])
    with changepw_tab:
        with st.form("changepw",clear_on_submit=True):
            oldpw = st.text_input("Enter old password",type="password")
            newpw1 = st.text_input("Enter new password",type="password")
            newpw2 = st.text_input("Repeate new password",type="password")
            changepw = st.form_submit_button("Change")
        if changepw:
            change_info = PasswordChangeData(oldpw, newpw1, newpw2)
            change_password(change_info)

        with change_api_tab:
            with st.form("changeapikey",clear_on_submit=True):
                oldpw = st.text_input("Enter your password",type="password")
                newapikey = st.text_input("Enter new OPENAI API KEY",type="password")
                change_api = st.form_submit_button("Change")
            if change_api:
                change_info = APIKeyChangeData(oldpw, newapikey)

                change_openai_apikey(change_info)
