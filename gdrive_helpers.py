from oauth2client.service_account import ServiceAccountCredentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import streamlit as st
from database import Database
import os
from tqdm import tqdm
import mysql

from dictclasses import StoredFileData

def google_auth() -> ServiceAccountCredentials:
    scope = ["https://www.googleapis.com/auth/drive"]
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["gmail_service_account"], scope)
    return credentials

def setup_pydrive() -> GoogleDrive:
    gauth = GoogleAuth()
    gauth.credentials = google_auth()
    drive = GoogleDrive(gauth)
    return drive

def download_pdf(username: str, lecture: str) -> bool:
    """Downloads the lecture PDF

    Returns:
        bool: True if it already exists
    """

    drive = setup_pydrive()
    db = Database()
    id = db.query("SELECT pdf_id from filestorage WHERE username = %s AND lecture = %s",(username,lecture))[0][0]
    if not os.path.isdir(f"tmp/{lecture}"):
        os.makedirs(f"tmp/{lecture}")
    if os.path.isfile(f"tmp/{lecture}/{lecture}.pdf"):
        return True
    file = drive.CreateFile({'id': id})
    file.GetContentFile(f"tmp/{lecture}/{lecture}.pdf")
    return False

def download_faiss_data(username: str, lecture: str):
    drive = setup_pydrive()
    db = Database()
    ids = db.query("SELECT index_faiss_id,index_pkl_id from filestorage WHERE username = %s AND lecture = %s",(username,lecture))[0]
    if not os.path.isdir(f"tmp/{lecture}"):
        os.makedirs(f"tmp/{lecture}")
    if not os.path.isfile("tmp/{lecture}/index.faiss"):
        for id, file_kind in zip(ids, ["faiss","pkl"]):
            file = drive.CreateFile({'id': id})
            # if file_kind == "pdf":
            #     file.GetContentFile("tmp/pdf.pdf")
            # else:
            file.GetContentFile(f"tmp/{lecture}/index.{file_kind}")
    else:
        return True

def create_folder(foldername: str, parent_folder_id: str=None, permissions: bool= False) -> (str | list[str], bool):
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

def upload_file_to_google(file_path: str, parent_folder_id: str, file_name: str) -> str:
    drive = setup_pydrive()

    file1 = drive.CreateFile({'title': file_name,
                              'parents': [{"id": parent_folder_id}]})
    file1.SetContentFile(file_path)
    file1.Upload()
    # file1.InsertPermission({"type":"user","role":"writer","value":st.secrets["gmail"]})
    return file1['id']

def upload_lecture_to_drive(username: str, lecture: str):
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
        db.execute_query(
            """UPDATE filestorage
            SET pdf_id = %s, index_faiss_id = %s, index_pkl_id= %s
            WHERE username = %s AND lecture = %s
            """,
            (pdf_id, index_faiss_id, index_pkl_id,username,lecture))
    else:
        db.add_filestorage(StoredFileData(username, lecture, pdf_id, index_faiss_id, index_pkl_id))

    return True


def delete_from_folder(folder_id: str):
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

def delete_database():
    cnx =  mysql.connector.connect(host="localhost",
                                    user=st.secrets["my_sql"]["mysql_user"],
                                password=st.secrets["my_sql"]["mysql_password"])
    cnx.cursor().execute(f"DROP DATABASE {st.secrets['my_sql']['mysql_dbName']}")

def reset_database(tables: list[str]=None):
    
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

def delete_all():
    delete_database()
    reset_drive()

def delete_lecture_from_drive(lecture):
    root_folder_id, root_existed = create_folder(st.secrets["my_sql"]["mysql_dbName"],permissions=True)
    user_folder_id, user_folder_existed = create_folder(st.session_state["username"], parent_folder_id=root_folder_id)
    lecture_folder_id, lecture_existed = create_folder(lecture, parent_folder_id=user_folder_id)
    delete_from_folder(lecture_folder_id)
    drive = setup_pydrive()
    file1 = drive.CreateFile({'id': lecture_folder_id})
    file1.Delete()