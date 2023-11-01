import json
import pandas as pd
import streamlit as st
import os 

# @st.cache_data
def load_history():
    history_path = "data/mockup_history.json"
    if os.path.isfile(history_path):
        historydb = pd.read_json("data/mockup_history.json")
    else:
        historydb = pd.DataFrame([{"prompt":None,
                      "message":None,
                      "username":None,
                      "lecture":None,
                      "language":None}])
        historydb.to_json("data/mockup_history.json",orient="records",indent=4)
    return historydb
    

def load_chat_history(username,lecture,newest_k=10):
        historydb = load_history()
        st.session_state.messages = []
        st.session_state.history = []
        filtered_history = historydb[(historydb["username"]==username) & (historydb["lecture"]==lecture)][:-newest_k]
        for msg in filtered_history.to_dict("records"):
            st.session_state.messages.append({"role":"user","content":msg["prompt"]})
            st.session_state.messages.append({"role":"assistant","content":msg["message"]})
            st.session_state.history.append((msg["prompt"],msg["message"]))

def save_history(message_info):
    historydb = pd.read_json("data/mockup_history.json").to_dict("records")
    historydb.append(message_info)
    pd.DataFrame(historydb).to_json("data/mockup_history.json",orient="records",indent=4)