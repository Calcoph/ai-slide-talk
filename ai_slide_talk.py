import pandas as pd
import streamlit as st
from auth_helpers import logout_user, render_login_register
from chat_helpers import render_chat_layout
from initialize import initialize_session_state
import os

@st.cache_data
def load_userdb():
    userdb_path = "data/mockup_userdb.json"
    if os.path.isfile(userdb_path):
        userdb = pd.read_json("data/mockup_userdb.json")
    else:
        userdb = pd.DataFrame([{"email":None,"username":None,"password":None,"OPENAI_API_KEY":None}])
        userdb.to_json(userdb_path,orient="records",indent=4)
    return userdb
    

st.title("Chat with Lecture Slides 💬")

initialize_session_state()

userdb = load_userdb()

if st.session_state["authentication_status"]:
    ###
    # CHAT FRONTEND
    ###
    logout = st.sidebar.button("Logout")
    if logout:
        logout_user()
    #logout = st.sidebar.button("Logout")
    st.subheader(f"Hey {st.session_state['username']} 👋")

    # st.subheader("REST OF FORNTEND GOES HERE")

    render_chat_layout()
else:
    ###
    # Login/Register FRONTEND
    ###
    render_login_register()
