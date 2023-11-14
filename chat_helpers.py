import streamlit as st
from dictclasses import FullMessage
from history_helpers import load_chat_history,save_history
from initialize import streamlit_setup_qa
from gdrive_helpers import download_faiss_data

def render_chat_layout():
    """Chat UI"""

    ## main page
    if (st.session_state["lecture"] and st.session_state["language"]) == False:
        st.success("⬅️ Select a language and a lecture on the side.")
        st.stop()
    
    for msg in st.session_state.messages:
        if msg["role"] != "AI Prof":
            st.chat_message(msg["role"]).write(msg["content"])
        else:
            st.chat_message(msg["role"], avatar="👩‍🏫").write(msg["content"])

    # if st.session_state["explainer"] == True:
    #     explainer_text = "activated"
    # else:
    #     explainer_text = "deactivated"
    st.chat_message("assistant").write(f"""You are chatting with the 
                                       **{st.session_state['lecture']}** slides in **{st.session_state['language']}**.
                                        How can I help you?""")

    if prompt := st.chat_input():
        #add user message to session_state messages
        st.session_state.messages.append({"role": "user", "content": prompt})
        #write in chat
        st.chat_message("user").write(prompt)
        with st.spinner("Thinking 🤔"):
            if st.session_state["explainer"] == False:   
                response = st.session_state["qa"]({"question": prompt, "chat_history":st.session_state["history"]})
                slidenumbers = [str(x.metadata["page"]) for x in response["source_documents"]]
                msg = {"role": "assistant", "content":f"""{response["answer"]} **The respective information can be found in slides {", ".join(slidenumbers)}**"""}
                st.session_state.messages.append(msg)
                st.session_state.history.append((prompt,response["answer"]))
                #write in chat
                st.chat_message("assistant").write(msg["content"])
            else:
                response = st.session_state["chatbot"]({"question":prompt,
                                                         "chat_history": []})
                                                         #st.session_state["history"][-1]})
                msg = {"role": "AI Prof", "content":response["text"]}
                st.session_state.messages.append(msg)
                st.chat_message("AI Prof",avatar="👩‍🏫").write(response["text"])
            
            message_info = FullMessage(
                    prompt,
                    msg["content"],
                    st.session_state["username"],
                    st.session_state["lecture"],
                    msg["role"],
                    st.session_state["language"],
                )
            save_history(message_info)
    st.session_state["explainer"] = st.toggle("👩‍🏫 AI Prof",help="If activated, the system gives open answers not depending on the lecture content.")

def render_lecture_selector():
    """Lecture selector UI"""

    with st.sidebar:
        with st.expander("Select a Lecture & Language"):
            with st.form("lecture_change"):
                lecture = st.selectbox("Select the lecture you want to chat with.", options=st.session_state["lecture_list"])
                language = st.radio("Choose language of Answer", options=["English","Spanish","German"], horizontal=True)
                lecture_change = st.form_submit_button("Change lecture & language")

        if lecture_change:
            st.session_state["lecture"] = lecture
            st.session_state["language"] = language
            load_chat_history(st.session_state["lecture"],
                            newest_k=10)
            with st.spinner("Downloading Data."):
                download_faiss_data(st.session_state["username"],st.session_state["lecture"])
                st.session_state["qa"] = streamlit_setup_qa()
