import openai
import streamlit as st
import pandas as pd
import os
import bcrypt
from cryptography.fernet import Fernet

def check_api_key(key):
    try:
        openai.api_key = key 
        openai.Completion.create(
        prompt="Test",
        model = "davinci",
            max_tokens=5)
        return True
    except Exception as e:
        #st.write(e)
        return False

def create_new_user(userinfo, check_key=True):
    userdb = pd.read_json("mockup_userdb.json")
    #check if api key is valid, can be disabled for development purposes, set "check_key" to False
    if not check_api_key(decrypt_api_key(userinfo["OPENAI_API_KEY"])) and check_key:
        st.error("Your OPENAI API-KEY is wrong. Check again.")
        st.stop()
    # ensure username to be unique
    if userinfo["username"] in list(userdb["username"]):
        st.error("Username already taken. Choose another one.")
        st.stop()
    #add user to database
    userdb = pd.concat([userdb,pd.DataFrame(userinfo,index=[0])])     
    userdb.to_json("mockup_userdb.json",orient="records",indent=4)
    st.success("You registered succesfully. Login with your credentials.")

def logout_user():
    os.environ["OPENAI_API_KEY"] = ""
    st.session_state["authentication_status"] = False
    st.session_state["username"] = None
    st.experimental_rerun()

def login_user(username,password):
    userdb = pd.read_json("mockup_userdb.json")
    st.write(userdb)
    try:
        query_res = userdb[userdb["username"]==username]["password"].iloc[0]
    except IndexError:
        st.warning("Username not correct.")
        st.stop()
    if bcrypt.checkpw(password.encode(),query_res.encode()):
        st.session_state["authentication_status"] = True
        st.session_state["username"] = username
        st.write(userdb[userdb["username"]==st.session_state["username"]]["OPENAI_API_KEY"])
        os.environ["OPENAI_API_KEY"] = decrypt_api_key(userdb[userdb["username"]==st.session_state["username"]]["OPENAI_API_KEY"].iloc[0])
        st.experimental_rerun()
    else:
        st.error("Password is wrong.")

def render_login_register():
    login_tab, register_tab = st.tabs(["**Login**", "**Register**"])
    with login_tab:
        with st.form("login", clear_on_submit=False): 
            username = st.text_input("Username")
            password = st.text_input("Password",type="password")  
            login = st.form_submit_button("Login")
        if login:
            login_user(username=username,password=password)

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
                        "OPENAI_API_KEY": encrypt_api_key(apikey)
                        }
            create_new_user(userinfo=userinfo,check_key=False)       

def decrypt_api_key(encrypted_api_key):
    encryption_key = st.secrets["encryption_key"]
    fernet = Fernet(encryption_key)
    return fernet.decrypt(encrypted_api_key).decode()

def encrypt_api_key(raw_api_key):
    encryption_key = st.secrets["encryption_key"]
    fernet = Fernet(encryption_key)
    return fernet.encrypt(raw_api_key.encode())                               