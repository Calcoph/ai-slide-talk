from datababe import Database
import pandas as pd
import streamlit as st
import os

# @st.cache_data
def load_history():
    # REPLACE WITH MYSQL
    db = Database(st.secrets["mysql_dbName"])
    #user_history = db.query("SELECT * FROM history WHERE %s",(st.session_state["username"],))
    user_history = db.query("SELECT * FROM history WHERE username = %s",
                            (st.session_state["username"],))
    return pd.DataFrame(user_history,columns=["id","prompt","message","username","lecture","language"])


def load_chat_history(lecture,newest_k=5):
        st.session_state.messages = []
        st.session_state.history = []
        filtered_history = st.session_state["userhistory"][st.session_state["userhistory"]["lecture"]==lecture]#[:-newest_k]
        for msg in filtered_history.to_dict("records"):
            st.session_state.messages.append({"role":"user","content":msg["prompt"]})
            st.session_state.messages.append({"role":"assistant","content":msg["message"]})
            st.session_state.history.append((msg["prompt"],msg["message"]))

def save_history(message_info):
    db = Database(st.secrets["mysql_dbName"])
    db.add_history(message_info)
    st.session_state["userhistory"] = pd.concat([st.session_state["userhistory"],pd.DataFrame(message_info, index=[0])]).reset_index(drop=True)   