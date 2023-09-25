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

def init_lecture():
    try:
        st.session_state["lecture"] = [x.split("_")[-1] for x in os.listdir("data/embeddings/")][0]
    except:
        st.error("**No Lecture uploaded. Go to the 'Upload Lecture' Tab on the side**")
        st.stop()
    
    return None

def streamlit_setup_explainer_bot():
    setup_explainer_bot(st.session_state["language"])

def streamlit_setup_qa():
    setup_qa(st.session_state["lecture"], st.session_state["language"])

def get_default_messages():
    [
        {
            "role": "assistant",
            "content": f"You are chatting with the {st.session_state['lecture']} slides in {st.session_state['language']}. How can I help you?"
        }
    ]

# This is a list instead of a dict because order of operations is important
# Values are lambdas so they are lazily evaluated
defaults = [
    ("history", lambda: []),
    ("explainer", lambda: False),
    ("language", lambda: "english"),
    ("lecture", init_lecture),
    ("messages", get_default_messages),
    ("qa", streamlit_setup_qa),
    ("chatbot", streamlit_setup_explainer_bot)
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
    vectorstore = FAISS.load_local(f"data/embeddings/local_faiss_{lecture}",embeddings=embeddings)
    

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


    
    qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0), vectorstore.as_retriever()
                                       ,combine_docs_chain_kwargs={"prompt": qa_prompt}, return_source_documents=True)
    
    return qa

@st.cache_resource()
def setup_explainer_bot(language):
    llm = ChatOpenAI()
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

    conversation = LLMChain(
        llm=llm,
        prompt=prompt,
        #verbose=True,
    )

    return conversation
