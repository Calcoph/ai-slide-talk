from langchain.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    MessagesPlaceholder,
    HumanMessagePromptTemplate,
)
import streamlit as st

from langchain.chains import LLMChain
from langchain.memory import ConversationBufferMemory
import os
from database import *

def init_lecture():
    st.session_state["lecture"] = st.session_state["lecture_list"][0]

def load_lecturenames():
    db = Database(st.secrets["mysql_dbName"])
    uploaded_lectures = db.query("SELECT lecture from filestorage WHERE username = %s",
                                                    (st.session_state["username"],))
    uploaded_lectures = set([x[0] for x in uploaded_lectures])

    if not uploaded_lectures:
        st.error("**No Lecture uploaded. Go to the 'Upload Lecture' Tab on the side**")
        st.stop()
    st.session_state["lecture_list"] = uploaded_lectures

def streamlit_setup_explainer_bot():
    return setup_explainer_bot(st.session_state["language"])

def streamlit_setup_qa():
    return setup_qa(st.session_state["lecture"], st.session_state["language"])

def get_default_messages():
    try:
        lecture = st.session_state['lecture']
        return [
            {
                "role": "assistant",
                "content": f"You are chatting with the {lecture} slides in {st.session_state['language']}. How can I help you?"
            }
        ]
    except KeyError:
        return [
            {
                "role": "assistant",
                "content": f"Couldn't load correctly. Do you have a valid OpenAI api token?"
            }
        ]

# This is a list instead of a dict because order of operations is important
# Values are lambdas so they are lazily evaluated
defaults = [
    ("history", lambda: []),
    ("explainer", lambda: False),
    ("language", lambda: False),
    ("lecture_list", load_lecturenames),
    ("lecture", lambda: False),
    ("messages", lambda: []),
    #("qa", streamlit_setup_qa),
    #("chatbot", streamlit_setup_explainer_bot),
    #("authentication_status", lambda: False)
]

def initialize_session_state():
    for (key, default_value) in defaults:
        if key not in st.session_state:
            value = default_value()
            if value is not None:
                st.session_state[key] = value

@st.cache_resource()
def setup_qa(lecture, language):

    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.load_local(f"tmp/{lecture}/embeddings",embeddings=embeddings)
    
    template = """Use the following pieces of context to answer the users question. \n
    If you don't know the answer, just say that you don't know, don't try to make up an answer.
    \n----------------\n{context}"""

    language_text = f"Your answer should be in {language}."

    template = template + language_text
    messages = [
    SystemMessagePromptTemplate.from_template(template),
    HumanMessagePromptTemplate.from_template("{question}")
    ]
    qa_prompt = ChatPromptTemplate.from_messages(messages)



    if vectorstore is None:
        return None
    else:
        qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0), vectorstore.as_retriever()
                                        ,combine_docs_chain_kwargs={"prompt": qa_prompt}, return_source_documents=True)

        return qa

@st.cache_resource()
def setup_explainer_bot(language):
    try:
        llm = ChatOpenAI()
    except Exception as e:
        llm = None
    prompt = ChatPromptTemplate(
        messages=[
            SystemMessagePromptTemplate.from_template(
                "You are a helpful college professor that explains difficult subjects to 10 year olds. "+
                f"Your answers should be in {language}" +
                """This is the previous conversation with the user: \n

                {chat_history}
                """),
            HumanMessagePromptTemplate.from_template("{question}")
        ]
    )

    if llm is None:
        conversation = None
    else:
        conversation = LLMChain(
            llm=llm,
            prompt=prompt,
            #verbose=True,
        )
    return conversation
