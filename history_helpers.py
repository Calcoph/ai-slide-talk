import json
import pandas as pd
import streamlit as st

def load_chat_history(username,newest_k=10):
        with open("data/mockup_history.json","r") as fp:
            historydb = json.load(fp=fp)
        st.session_state.messages = []
        for msg in historydb[:-newest_k]:
            if msg["username"] == username: #and msg["lecture"] == lecture:
                st.session_state.messages.append({"role":"user","content":msg["prompt"]})
                st.session_state.messages.append({"role":"assistant","content":msg["message"]})

def save_history(message_info):
    historydb = pd.read_json("data/mockup_history.json").to_dict("records")
    historydb.append(message_info)
    pd.DataFrame(historydb).to_json("data/mockup_history.json",orient="records",indent=4)