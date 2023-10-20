import streamlit as st
import pandas as pd 
from auth_helpers import *

userdb = pd.read_json("data/mockup_userdb.json")

if st.session_state["authentication_status"] is True:
    logout = st.sidebar.button("Logout")
    if logout:
        logout_user()

    changepw_tab, change_api_tab = st.tabs(["**Change Password**", "**Change OPENAI API KEY**"])
    with changepw_tab:
        with st.form("changepw",clear_on_submit=True):
            oldpw = st.text_input("Enter old password",type="password")
            newpw1 = st.text_input("Enter new password",type="password")
            newpw2 = st.text_input("Repeate new password",type="password")
            changepw = st.form_submit_button("Change")
        if changepw:
            change_info = {"oldpw":oldpw,
                        "newpw1":newpw1,
                        "newpw2":newpw2}
            change_password(change_info)

                    
        with change_api_tab:
            with st.form("changeapikey",clear_on_submit=True):
                oldpw = st.text_input("Enter your password",type="password")
                newapikey = st.text_input("Enter new OPENAI API KEY",type="password")
                change_api = st.form_submit_button("Change")
            if change_api:
                change_info = {"oldpw":oldpw,
                               "newapikey":newapikey}
                
                change_openai_apikey(change_info=change_info)
else:
    st.warning("Login on the Mainpage.")