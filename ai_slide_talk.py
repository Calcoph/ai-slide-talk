import streamlit as st
from auth_helpers import check_login
from chat_helpers import render_chat_layout, render_lecture_selector
from initialize import initialize_session_state, check_secrets_file, render_secrets_creator, initialize_session_state_before_login

initialize_session_state_before_login()

if not check_secrets_file():
    render_secrets_creator()

st.title("SlideChatter 💬")
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
