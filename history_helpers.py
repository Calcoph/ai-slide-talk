from database import Database
import pandas as pd
import streamlit as st
import os

from dictclasses import FullMessage

# @st.cache_data
def load_history() -> pd.DataFrame:
    """Returns the message history"""

    db = Database()
    user_history = db.query("SELECT * FROM history WHERE username = %s",
                            (st.session_state["username"],))
    return pd.DataFrame(user_history,columns=["id","prompt","message","username","lecture","role","language"])


def load_chat_history(lecture: str):
    """Loads the message history in the session"""

    st.session_state.messages = []
    st.session_state.history = []
    filtered_history = st.session_state["userhistory"][st.session_state["userhistory"]["lecture"]==lecture]#[:-newest_k]
    for msg in filtered_history.to_dict("records"):
        st.session_state.messages.append({"role":"user","content":msg["prompt"]})
        st.session_state.messages.append({"role":msg["role"],"content":msg["message"]})
        st.session_state.history.append((msg["prompt"],msg["message"]))

def save_history(message_info: FullMessage):
    """Adds a message to the history"""

    db = Database()
    db.add_history(message_info)
    st.session_state["userhistory"] = load_history()
    

