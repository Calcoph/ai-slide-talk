import streamlit as st
import pandas as pd
from auth_helpers import *
import os 
import bcrypt

st.title("Chat with Lecture Slides 💬")

# needs to be added to sessionstate init
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

userdb = pd.read_json("mockup_userdb.json")
###
# Login/Register FRONTEND
###
if st.session_state["authentication_status"] in [False, None]:
    render_login_register()
###
# CHAT FRONTEND
###                         
if st.session_state["authentication_status"] is True:
    logout = st.sidebar.button("Logout")
    if logout:
        logout_user()
    #logout = st.sidebar.button("Logout")
    st.subheader(f"Hey {st.session_state['username']} 👋")

    st.subheader("REST OF FORNTEND GOES HERE")


