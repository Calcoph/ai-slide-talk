import streamlit as st
from initialize import *
import os

if "history" not in st.session_state:
    st.session_state["history"] = []

if "explainer" not in st.session_state:
    st.session_state["explainer"] = False

if "language" not in st.session_state:
    st.session_state["language"] = "english"

if "lecture" not in st.session_state:
    try:
        st.session_state["lecture"] = [x.split("_")[-1] for x in os.listdir("data/embeddings/")][0]
    except:
        st.error("**No Lecture uploaded. Go to the 'Upload Lecture' Tab on the side**")
        st.stop()

if "messages" not in st.session_state:
    st.session_state["messages"] =  [{"role": "assistant", "content": 
                                    f"You are chatting with the {st.session_state['lecture']} slides in {st.session_state['language']}. How can I help you?"}]

if "qa" not in st.session_state:
    st.session_state["qa"] = setup_qa(st.session_state["lecture"], st.session_state["language"])

if "chatbot" not in st.session_state:
    st.session_state["chatbot"] = setup_explainer_bot(st.session_state["language"])
