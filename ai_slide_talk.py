import pandas as pd
import streamlit as st
from auth_helpers import check_login, load_userdb
from chat_helpers import render_chat_layout
from initialize import initialize_session_state

st.title("Chat with Lecture Slides 💬")

init_variables = ["authentication_status", "username"]
for var in init_variables:
    if var not in st.session_state:
        st.session_state[var] = None


userdb = load_userdb()

if check_login(render_login_template=True):
    
    initialize_session_state()
    ###
    # CHAT FRONTEND
    ###
    st.subheader(f"Hey {st.session_state['username']} 👋")

    render_chat_layout()