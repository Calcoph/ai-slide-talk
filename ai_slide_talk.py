import pandas as pd
import streamlit as st
from auth_helpers import check_login
from chat_helpers import render_chat_layout
from initialize import initialize_session_state
import os

@st.cache_data()
def load_userdb():
    userdb_path = "data/mockup_userdb.json"
    if os.path.isfile(userdb_path):
        userdb = pd.read_json("data/mockup_userdb.json")
    else:
        if not os.path.isdir(f"data"):
            os.makedirs(f"data")
        userdb = pd.DataFrame([{"email":None,"username":None,"password":None,"OPENAI_API_KEY":None}])
        userdb.to_json(userdb_path,orient="records",indent=4)
    return userdb
    

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