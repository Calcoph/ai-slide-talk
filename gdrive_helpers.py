from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import streamlit as st
from database import Database
import os
from tqdm import tqdm
import mysql

def google_auth():
    scope = ["https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gmail_service_account"], scope)
    return credentials

def setup_pydrive():
    gauth = GoogleAuth()
    gauth.credentials = google_auth()
    drive = GoogleDrive(gauth)
    return drive

def download_pdf(username,lecture):
    drive = setup_pydrive()
    db = Database()
    id = db.query("SELECT pdf_id from filestorage WHERE username = %s AND lecture = %s",(username,lecture))[0][0]
    if not os.path.isdir(f"tmp/{lecture}"):
        os.makedirs(f"tmp/{lecture}")
    elif os.path.isfile(f"tmp/{lecture}/{lecture}.pdf"):
        return True
    else:
        pass
    file = drive.CreateFile({'id': id})
    file.GetContentFile(f"tmp/{lecture}/{lecture}.pdf")


def download_faiss_data(username,lecture):
    drive = setup_pydrive()
    db = Database()
    ids = db.query("SELECT index_faiss_id,index_pkl_id from filestorage WHERE username = %s AND lecture = %s",(username,lecture))[0]
    if not os.path.isdir(f"tmp/{lecture}"):
        #os.makedirs(f"tmp/{lecture}")
        os.makedirs(f"tmp/{lecture}")
    elif os.path.isfile("index.faiss"):
        return True
    else:
        pass
    for id, file_kind in zip(ids, ["faiss","pkl"]):
        file = drive.CreateFile({'id': id})
        # if file_kind == "pdf":
        #     file.GetContentFile("tmp/pdf.pdf")
        # else:
        file.GetContentFile(f"tmp/{lecture}/index.{file_kind}")
    return True

def create_folder(foldername, parent_folder_id=None, permissions = False):
    drive = setup_pydrive()
    search_term = f"mimeType='application/vnd.google-apps.folder'"
    if parent_folder_id != None:
        search_term +=f"and '{parent_folder_id}' in parents"
    content_list = drive.ListFile({'q': search_term}).GetList()
    content_names = [x["title"] for x in content_list]
    if foldername in content_names:
        return list(filter(lambda item: item['title'] == foldername, content_list))[0]["id"], True
    else:
        file_metadata_root = {
        'title': foldername,
        'mimeType': 'application/vnd.google-apps.folder',
        "parents":[{"id":parent_folder_id}]
    }
    if parent_folder_id == None:
        del file_metadata_root['parents']
    folder = drive.CreateFile(file_metadata_root)
    folder.Upload()
    if permissions:
        folder.InsertPermission({"type":"user","role":"writer","value":st.secrets["gmail"]["gmail_email"]})
    return folder["id"], False

def upload_file_to_google(file_path,parent_folder_id, file_name):
    drive = setup_pydrive()
    
    file1 = drive.CreateFile({'title': file_name,
                              'parents': [{"id": parent_folder_id}]})
    file1.SetContentFile(file_path)
    file1.Upload()
    # file1.InsertPermission({"type":"user","role":"writer","value":st.secrets["gmail"]})
    return file1['id']

def upload_lecture_to_drive(username, lecture):
    root_folder_id, root_existed = create_folder(st.secrets["my_sql"]["mysql_dbName"],permissions=True)
    user_folder_id, user_folder_existed = create_folder(username, parent_folder_id=root_folder_id)
    lecture_folder_id, lecture_existed = create_folder(lecture, parent_folder_id=user_folder_id)

    if lecture_existed:
        delete_from_folder(lecture_folder_id)

    pdf_id = upload_file_to_google(f"tmp/uploaded_files/{lecture}.pdf",
                                lecture_folder_id,f"{lecture}.pdf")
    index_faiss_id = upload_file_to_google("tmp/uploaded_files/index.faiss",
                            parent_folder_id=lecture_folder_id,
                            file_name="index.faiss")
    index_pkl_id = upload_file_to_google("tmp/uploaded_files/index.pkl",
                            parent_folder_id=lecture_folder_id,
                            file_name="index.pkl")

    db = Database()
    if lecture_existed:
        db.update_filestorage("UPDATE filestorage SET pdf_id = %s, index_faiss_id = %s, index_pkl_id= %s WHERE username = %s AND lecture = %s""",(pdf_id, index_faiss_id, index_pkl_id,username,lecture))
    else:
        db.add_filestorage((username,lecture,pdf_id, index_faiss_id, index_pkl_id))

    return True


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
        
def reset_database(tables=None):
    cnx =  mysql.connector.connect(host="localhost",
                                user=st.secrets["my_sql"]["mysql_user"],
                                password=st.secrets["my_sql"]["mysql_password"],
                                database=st.secrets["my_sql"]['mysql_dbName']
                                )
    if tables == None:
        tables = [
        "users",
        "history",
        "filestorage"]
    with cnx.cursor() as cursor:

        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            cnx.commit()

def delete_all(tables):
    reset_database(tables)
    reset_drive()