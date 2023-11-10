import streamlit as st
from history_helpers import load_chat_history,save_history
from initialize import streamlit_setup_qa
from gdrive_helpers import download_faiss_data

class FullMessage:
    def __init__(self, prompt: str, message: str, username: str, lecture: str, language: str) -> None:
        self.prompt = prompt
        self.message = message
        self.username = username
        self.lecture = lecture
        self.language = language

    def to_dict(self) -> dict[str, str]:
        {
            "prompt": self.prompt,
            "message": self.message,
            "username": self.username,
            "lecture": self.lecture,
            "language": self.language
        }

def render_chat_layout():
    """Chat UI"""

    ## main page
    if (st.session_state["lecture"] and st.session_state["language"]) == False:
        st.success("⬅️ Select a language and a lecture on the side.")
        st.stop()

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])
    st.chat_message("assistant").write(f"You are chatting with the **{st.session_state['lecture']}** slides in **{st.session_state['language']}**. How can I help you?")

    if prompt := st.chat_input():
        #add user message to session_state messages
        st.session_state.messages.append({"role": "user", "content": prompt})
        #write in chat
        st.chat_message("user").write(prompt)
        with st.spinner("Thinking 🤔"):
            response = st.session_state["qa"]({"question": prompt, "chat_history":st.session_state["history"]})
            slidenumbers = [str(x.metadata["page"]) for x in response["source_documents"]]
            msg = {"role": "assistant", "content":f"""{response["answer"]} **The respective information can be found in slides {", ".join(slidenumbers)}**"""}
            st.session_state.messages.append(msg)
            st.session_state.history.append((prompt,response["answer"]))
            #write in chat
            st.chat_message("assistant").write(msg["content"])

            message_info = FullMessage(
                prompt,
                msg["content"],
                st.session_state["username"],
                st.session_state["lecture"],
                st.session_state["language"]
            )

            save_history(message_info)

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
