import streamlit as st
import os
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS


def create_faiss_store(pdf_path: str, lecturename: str):
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
        vectorstore.save_local(f"data/embeddings/local_faiss_{lecturename}")
        st.success("Finished.")
    return vectorstore

def save_uploadedfile(uploadedfile):
    with open(os.path.join("data/pdfs",uploadedfile.name),"wb") as f:
        f.write(uploadedfile.getbuffer())
    return None

with st.form("lectureupload"):
    lecturename = st.text_input("Enter the Lecturename")
    
    pdf = st.file_uploader("Upload your lecture slides.",type="pdf")
    submit = st.form_submit_button("Upload")

if submit:
    if "_" in lecturename:
        st.warning("The Lecturename must not contain an underscore  ( _ ) .")
        st.stop()
    save_uploadedfile(pdf)
    with st.spinner("Processing.."):
        create_faiss_store(f"data/pdfs/{pdf.name}",lecturename=lecturename)