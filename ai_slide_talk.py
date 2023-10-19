import pandas as pd
import streamlit as st
from auth_helpers import logout_user, render_login_register
from chat_helpers import render_chat_layout
from initialize import initialize_session_state

st.title("Chat with Lecture Slides 💬")

initialize_session_state()

userdb = pd.read_json("data/mockup_userdb.json")

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
