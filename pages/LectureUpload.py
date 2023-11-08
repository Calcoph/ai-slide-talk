import streamlit as st
import os
from langchain.document_loaders import PyPDFLoader,PDFPlumberLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from auth_helpers import logout_user,check_login
from initialize import load_lecturenames
from gdrive_helpers import upload_lecture_to_drive

def create_faiss_store(pdf_path):
    loader = PyPDFLoader(pdf_path)
    pages = loader.load_and_split()
    text_splitter = CharacterTextSplitter(separator = "\n", chunk_size = 1000, 
                                            chunk_overlap  = 200, length_function = len)
    docs = text_splitter.split_documents(pages)
    for doc in docs:
        doc.metadata["page"] +=1
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(docs, embeddings)
    faiss_path = "tmp/uploaded_files/"
    if not os.path.isdir(faiss_path):
        os.makedirs(faiss_path)
    vectorstore.save_local(faiss_path)
    return vectorstore

def save_uploadedfile(uploadedfile,lecturename):
    upload_path = "tmp/uploaded_files"
    if not os.path.isdir(upload_path):
        os.makedirs(upload_path)
    with open(os.path.join(upload_path,f"{lecturename}.pdf"),"wb") as f:
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
                        lecturename=lecturename)

        with st.spinner("Processing.."):
            with st.empty():
                st.info("Creating Embeddings")
                create_faiss_store(f"tmp/uploaded_files/{lecturename}.pdf")

                st.info("Uploading Data")
                upload_lecture_to_drive(st.session_state["username"],
                                    lecture=lecturename)
                load_lecturenames()
                st.success("Upload successful")
                
            