import pandas as pd
import streamlit as st
from auth_helpers import check_login
from chat_helpers import render_chat_layout, render_lecture_selector
from initialize import initialize_session_state

st.title("Chat with Lecture Slides 💬")

init_variables = ["authentication_status", "username"]
for var in init_variables:
    if var not in st.session_state:
        st.session_state[var] = None

if check_login(render_login_template=True):
    
    initialize_session_state()
    ###
    # CHAT FRONTEND
    ###
    st.subheader(f"Hey {st.session_state['username']} 👋")

    # lecture selection in sidebar
    render_lecture_selector()

    #main chat window
    render_chat_layout()