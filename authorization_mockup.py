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
    login_tab, register_tab = st.tabs(["**Login**", "**Register**"])
    with login_tab:
        with st.form("login", clear_on_submit=True): 
            username = st.text_input("Username")
            password = st.text_input("Password",type="password")  
            login = st.form_submit_button("Login")

        if login:
            try:
                query_res = userdb[userdb["username"]==username]["password"].iloc[0]
            except IndexError:
                st.warning("Username not correct.")
                st.stop()
            if bcrypt.checkpw(password.encode(),query_res.encode()):
                st.session_state["authentication_status"] = True
                st.session_state["username"] = username
                st.experimental_rerun()
            else:
                st.error("Password is wrong.")

    with register_tab:
        with st.form("register", clear_on_submit=True):   
            st.subheader("Register")
            email = st.text_input("E-Mail")
            username = st.text_input("Username")
            apikey = st.text_input("OPENAI-API KEY",type="password")
            password = st.text_input("Password",type="password")
            register = st.form_submit_button("Register")
        if register:
            salt = bcrypt.gensalt()
            userinfo = {"email": email,
                        "username":username,
                        "password": bcrypt.hashpw(password=password.encode(),salt=salt),
                        "OPENAI_API_KEY": apikey
                        }
            create_new_user(userinfo=userinfo,check_key=False)                                      

###
# CHAT FRONTEND
###                         
if st.session_state["authentication_status"] is True:
    logout = st.sidebar.button("Logout")
    st.subheader(f"Hey {st.session_state['username']} 👋")
    os.environ["OPENAI_API_KEY"] = userdb[userdb["username"]==st.session_state["username"]]["OPENAI_API_KEY"].iloc[0]

    st.subheader("REST OF FORNTEND GOES HERE")
    
    if logout:
        os.environ["OPENAI_API_KEY"] = ""
        st.session_state["authentication_status"] = False
        st.session_state["username"] = None
        st.experimental_rerun()

    