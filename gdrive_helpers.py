from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import streamlit as st
from database import Database
import os
from tqdm import tqdm

def google_auth():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
            "https://www.googleapis.com/auth/drive"]

    input_dict = {
    "type": "service_account",
    "project_id": st.secrets["project_id"],
    "private_key_id": st.secrets["private_key_id"],
    "private_key": st.secrets["private_key"],
    "client_email": st.secrets["client_email"],
    "client_id": st.secrets["client_id"],
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": st.secrets["client_x509_cert_url"]}   
    
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(input_dict, scope)
    return credentials

def setup_pydrive():
    gauth = GoogleAuth()
    gauth.credentials = google_auth()
    drive = GoogleDrive(gauth)
    return drive


def get_lecture_data(username,lecture):
    drive = setup_pydrive()
    db = Database(st.secrets["mysql_dbName"])
    ids = db.query("SELECT index_faiss_id,index_pkl_id from filestorage WHERE username = %s AND lecture = %s",(username,lecture))[0]
    if not os.path.isdir(f"tmp/{lecture}"):
        #os.makedirs(f"tmp/{lecture}")
        os.makedirs(f"tmp/{lecture}/embeddings")
    else:
        return True
    for id, file_kind in zip(ids, ["faiss","pkl"]):
        file = drive.CreateFile({'id': id})
        # if file_kind == "pdf":
        #     file.GetContentFile("tmp/pdf.pdf")
        # else:
        file.GetContentFile(f"tmp/{lecture}/embeddings/index.{file_kind}")
    return True


def create_folder(foldername,parent_folder_id=None):
    drive = setup_pydrive()

    folderlist = (drive.ListFile  ({'q': "mimeType='application/vnd.google-apps.folder' and trashed=false"}).GetList())

    titlelist =  [x['title'] for x in folderlist]
    if foldername in titlelist:
        for item in folderlist:
            if item['title']==foldername:
                return item['id'], True
  
    file_metadata_root = {
        'title': foldername,
        'mimeType': 'application/vnd.google-apps.folder',
        "parents":[{"id":parent_folder_id}]
    }
    if parent_folder_id == None:
        del file_metadata_root['parents']
    user_root_folder = drive.CreateFile(file_metadata_root)
    user_root_folder.Upload()
    # user_root_folder.InsertPermission({"type":"user","role":"writer","value":st.secrets["gmail"]})
        
    return user_root_folder['id'], False

def upload_file_to_google(file_path,parent_folder_id, file_name):
    drive = setup_pydrive()
    
    file1 = drive.CreateFile({'title': file_name,
                              'parents': [{"id": parent_folder_id}]})
    file1.SetContentFile(file_path)
    file1.Upload()
    # file1.InsertPermission({"type":"user","role":"writer","value":st.secrets["gmail"]})
    return file1['id']

def upload_lecture_to_drive(username,lecturename):
    # Step 1: Check if userfolder exists
    st.toast("Uploading Lecture")
    user_root_folder_id, existed_root = create_folder(username)
    # Step 2: Check if lecture folder exists
    lecture_folder_id, existed_lecture = create_folder(lecturename,
                                                    parent_folder_id=user_root_folder_id)
    
    if existed_lecture:
        delete_from_folder(lecture_folder_id)
    # Step3: upload pdf
    pdf_folder, existed_pdf = create_folder("pdfs",parent_folder_id=lecture_folder_id)
    pdf_id = upload_file_to_google(f"tmp/uploaded_files/{lecturename}.pdf",pdf_folder,f"{lecturename}.pdf")
    # Step 4 create embeddings folder
    embeddings_folder, existed_embeddings = create_folder("embeddings",parent_folder_id=lecture_folder_id)
    st.toast("Uploading Embeddings")
    index_faiss_id = upload_file_to_google("tmp/uploaded_files/index.faiss",
                        parent_folder_id=embeddings_folder,
                        file_name="index.faiss")
    index_pkl_id = upload_file_to_google("tmp/uploaded_files/index.pkl",
                        parent_folder_id=embeddings_folder,
                        file_name="index.pkl")
    db = Database(st.secrets["mysql_dbName"])
    
    if existed_lecture:
        db.update_filestorage("UPDATE filestorage SET pdf_id = %s, index_faiss_id = %s, index_pkl_id= %s WHERE username = %s AND lecture = %s""",(pdf_id, index_faiss_id, index_pkl_id,username,lecturename))
    else:
        db.add_filestorage((username,lecturename,pdf_id, index_faiss_id, index_pkl_id))
    return pdf_id, index_faiss_id, index_pkl_id


def delete_from_folder(folder_id):
    drive = setup_pydrive()
    files = drive.ListFile({'q': f"'{folder_id}' in parents"}).GetList()
    for file in files:
        file1 = drive.CreateFile({'id': file["id"]})
        file1.Delete()
        
def reset_drive():
    drive = setup_pydrive()
    file_list = drive.ListFile({'q': "trashed=false"}).GetList()
    for file in tqdm(file_list):
        file1 = drive.CreateFile({'id': file["id"]})
        file1.Delete()
