import streamlit as st
import pandas as pd
from auth_helpers import render_login_register, logout_user
# from initialize import *
from chat_helpers import render_chat_layout
import os 

st.title("Chat with Lecture Slides 💬")

# needs to be added to sessionstate init
if "authentication_status" not in st.session_state:
    st.session_state["authentication_status"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

userdb_path = "data/mockup_userdb.json"
if os.path.isfile(userdb_path):
    userdb = pd.read_json("data/mockup_userdb.json")
else:
    pd.DataFrame([{"email":None,"username":None,"password":None,"OPENAI_API_KEY":None}]).to_json(userdb_path,orient="records",indent=4)
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
    
    # st.subheader("REST OF FORNTEND GOES HERE")

    render_chat_layout()

    