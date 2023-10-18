import streamlit as st
from history_helpers import load_chat_history,save_history

def render_chat_layout():
        # loads the messages of the user in "st.session_state.messages"
        load_chat_history(st.session_state["username"],newest_k=10)

        for msg in st.session_state.messages:
            st.chat_message(msg["role"]).write(msg["content"])

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
                                    "lecture":"API",
                                    "language":"English",
                                    }
            save_history(message_info)

