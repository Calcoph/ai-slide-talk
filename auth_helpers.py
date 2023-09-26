import openai
import streamlit as st
import pandas as pd



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
    if not check_api_key(userinfo["OPENAI_API_KEY"]) and check_key:
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
