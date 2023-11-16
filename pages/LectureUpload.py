import streamlit as st
from auth_helpers import check_login
from initialize import load_lecturenames
from gdrive_helpers import upload_lecture_to_drive
from upload_helpers import *

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="documentation\SlideChatter.ico"
)


if check_login():
    st.header("Lecture Upload")
    with st.form("lectureupload"):
        lecturename_upload = st.text_input("Enter the Lecturename")
        pdf = st.file_uploader("Upload your lecture slides.",type="pdf")
        submit_upload = st.form_submit_button("Upload")
        

    if submit_upload:
        if not lecturename_upload.isalnum():
            st.error("Lecturenames must only contain letters and numbers.")
            st.stop()
        if pdf == None:
            st.error("Upload a pdf")
            st.stop()
        save_uploadedfile(pdf,
                        lecturename=lecturename_upload)

        with st.spinner("Processing.."):
            with st.empty():
                if not check_if_lecture_exists(lecturename_upload):
                    st.info("Creating Embeddings")
                    create_faiss_store(f"tmp/uploaded_files/{lecturename_upload}.pdf")

                    st.info("Uploading Data")
                    upload_lecture_to_drive(st.session_state["username"],
                                        lecture=lecturename_upload)
                    load_lecturenames()
                    st.success("Upload successful")
                else:
                    st.error("Lecturename already taken, choose a different one. If you want to overwrite the lecture. Delete it first.")
                
    with st.expander("Delete Lecture",expanded=False):
        with st.form("lecture_delete"):
            st.warning("Deleting the lecture will also delete your chat history with the lecture.")
            lecturename = st.selectbox("Select the lecture you want to delete.", options=st.session_state["lecture_list"])
            submit_delete = st.form_submit_button("Delete")

    if submit_delete:
        with st.empty():
            st.info("Deleting..")
            delete_lecture(lecturename=lecturename)
            st.success("Successfully deleted lecture.")