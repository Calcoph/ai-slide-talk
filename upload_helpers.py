import os
from langchain.document_loaders import PyPDFLoader,PDFPlumberLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS

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