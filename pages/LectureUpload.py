import streamlit as st
from auth_helpers import check_login
from initialize import load_lecturenames
from gdrive_helpers import upload_lecture_to_drive
from upload_helpers import save_uploadedfile, create_faiss_store,delete_lecture

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
        save_uploadedfile(pdf,
                        lecturename=lecturename_upload)

        with st.spinner("Processing.."):
            with st.empty():
                st.info("Creating Embeddings")
                create_faiss_store(f"tmp/uploaded_files/{lecturename_upload}.pdf")

                st.info("Uploading Data")
                upload_lecture_to_drive(st.session_state["username"],
                                    lecture=lecturename_upload)
                load_lecturenames()
                st.success("Upload successful")
                
    with st.expander("Delete Lecture",expanded=False):
        with st.form("lecture_delete"):
            lecturename = st.selectbox("Select the lecture you want to delete.", options=st.session_state["lecture_list"])
            submit_delete = st.form_submit_button("Delete")

    if submit_delete:
        with st.empty():
            st.info("Deleting..")
            delete_lecture(lecturename=lecturename)
            st.success("Successfully deleted lecture.")