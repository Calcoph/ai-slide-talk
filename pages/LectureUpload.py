import streamlit as st
import os
from langchain.document_loaders import PyPDFLoader,PDFPlumberLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from auth_helpers import logout_user,check_login
from initialize import load_lecturenames

def create_faiss_store(pdf_path: str, lecturename: str,username):
    with st.empty():
        st.info("Transforming PDF to Documents.")
        loader = PyPDFLoader(pdf_path)
        pages = loader.load_and_split()
        text_splitter = CharacterTextSplitter(separator = "\n", chunk_size = 1000, 
                                                chunk_overlap  = 200, length_function = len)
        docs = text_splitter.split_documents(pages)
        for doc in docs:
            doc.metadata["page"] +=1
        st.info("Creating Embeddings.")
        embeddings = OpenAIEmbeddings()
        vectorstore = FAISS.from_documents(docs, embeddings)
        if not os.path.isdir(f"data/embeddings/{username}"):
            os.makedirs(f"data/embeddings/{username}")
        vectorstore.save_local(f"data/embeddings/{st.session_state['username']}/faiss_{lecturename}")
        st.success("Finished.")
    return vectorstore

def save_uploadedfile(uploadedfile,lecturename, username):
    if not os.path.isdir(f"data/pdfs/{username}"):
        os.makedirs(f"data/pdfs/{username}")
    with open(os.path.join(f"data/pdfs/{username}/",f"{lecturename}.pdf"),"wb") as f:
        f.write(uploadedfile.getbuffer())
    return None

if check_login():
    st.header("Lecture Upload")
    with st.form("lectureupload"):
        lecturename = st.text_input("Enter the Lecturename")
        pdf = st.file_uploader("Upload your lecture slides.",type="pdf")
        submit = st.form_submit_button("Upload")

    if submit:
        if "_" in lecturename:
            st.warning("The Lecturename must not contain an underscore  ( _ ) .")
            st.stop()
        save_uploadedfile(pdf,
                        lecturename=lecturename,
                        username=st.session_state["username"])

        with st.spinner("Processing.."):
            create_faiss_store(f"data/pdfs/{st.session_state['username']}/{lecturename}.pdf",
                            lecturename=lecturename,
                            username=st.session_state["username"])
            load_lecturenames()