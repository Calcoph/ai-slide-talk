import json
import pandas as pd
import streamlit as st
import os

# @st.cache_data
def load_history(username):
    # REPLACE WITH MYSQL
    history_path = "data/mockup_history.json"
    if os.path.isfile(history_path):
        # REPLACE WITH MYSQL
        historydb = pd.read_json("data/mockup_history.json")
        return historydb[historydb["username"]==username]
    else:
        historydb = pd.DataFrame([{"prompt":None,
                      "message":None,
                      "username":None,
                      "lecture":None,
                      "language":None}])
        # REPLACE WITH MYSQL
        historydb.to_json("data/mockup_history.json",orient="records",indent=4)
        return historydb
    

def load_chat_history(lecture,newest_k=10):
        st.session_state.messages = []
        st.session_state.history = []
        filtered_history = st.session_state["userhistory"][st.session_state["userhistory"]["lecture"]==lecture]#[:-newest_k]
        for msg in filtered_history.to_dict("records"):
            st.session_state.messages.append({"role":"user","content":msg["prompt"]})
            st.session_state.messages.append({"role":"assistant","content":msg["message"]})
            st.session_state.history.append((msg["prompt"],msg["message"]))

def save_history(message_info):
    st.session_state["userhistory"] = pd.concat([st.session_state["userhistory"],pd.DataFrame(message_info, index=[0])]).reset_index(drop=True)
    # REPLACE WITH MYSQL
    historydb = pd.read_json("data/mockup_history.json")
    # REPLACE WITH MYSQL
    pd.concat([historydb,pd.DataFrame(message_info, index=[0])]).reset_index(drop=True).to_json("data/mockup_history.json",orient="records",indent=4)