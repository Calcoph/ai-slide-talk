import json
import pandas as pd
import streamlit as st
import os 

def load_chat_history(username,lecture,newest_k=10):
        history_path = "data/mockup_history.json"
        if os.path.isfile(history_path):
            with open(history_path,"r") as fp:
                historydb = json.load(fp=fp)
        else:
            with open(history_path,"w") as fp:
                json.dump([],fp=fp)
            historydb = []
        ##
        ### Error in logic. Parses the latest 10 messages, if none is by the lecture and user
        ##
        for msg in historydb[:-newest_k]:
            if msg["username"] == username and msg["lecture"] == lecture:
                st.session_state.messages.append({"role":"user","content":msg["prompt"]})
                st.session_state.messages.append({"role":"assistant","content":msg["message"]})

def save_history(message_info):
    historydb = pd.read_json("data/mockup_history.json").to_dict("records")
    historydb.append(message_info)
    pd.DataFrame(historydb).to_json("data/mockup_history.json",orient="records",indent=4)