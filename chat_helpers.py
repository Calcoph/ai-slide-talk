import streamlit as st
from history_helpers import load_chat_history,save_history

def render_chat_layout():
    if "lecture" not in st.session_state:
        st.session_state["lecture"] = "API"
    if "language" not in st.session_state:
        st.session_state["language"] = "English"
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    with st.sidebar:
        with st.expander("Select a Lecture & Language"):
            with st.form("lecture_change"):
                st.session_state["lecture"] = st.selectbox("Select the lecture you want to chat with.", options=["API","MdD"])
                st.session_state["language"] = st.radio("Choose language of Answer", options=["English","Spanish","German"], horizontal=True)
                lecture_change = st.form_submit_button("Change lecture & language")
        if lecture_change:
            load_chat_history(st.session_state["username"],
                            st.session_state["lecture"],
                            newest_k=10)
            
    load_chat_history(st.session_state["username"],
                            st.session_state["lecture"],
                            newest_k=10)
    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    st.chat_message("assistant").write(f"You are chatting with the **{st.session_state['lecture']}** slides in **{st.session_state['language']}**. How can I help you?")
    
    if prompt := st.chat_input():
        #add user message to session_state messages
        st.session_state.messages.append({"role": "user", "content": prompt})
        #write in chat
        st.chat_message("user").write(prompt)
        
        #simulates the response of the AI
        msg = {"role":"assistant",
            "content":"This is a mockup message."}
        # add AI response to session_state messages
        st.session_state.messages.append(msg)
        #write in chat
        st.chat_message("assistant").write(msg["content"])

        message_info = {"prompt":prompt,"message":msg["content"],
                                "username":st.session_state["username"],
                                "lecture": st.session_state["lecture"],
                                "language":st.session_state["language"],
                                }
        save_history(message_info)

