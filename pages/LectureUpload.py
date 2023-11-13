import streamlit as st
from auth_helpers import check_login
from initialize import load_lecturenames
from gdrive_helpers import upload_lecture_to_drive
from upload_helpers import save_uploadedfile, create_faiss_store

if check_login():
    st.header("Lecture Upload")
    with st.form("lectureupload"):
        lecturename = st.text_input("Enter the Lecturename")
        pdf = st.file_uploader("Upload your lecture slides.",type="pdf")
        submit = st.form_submit_button("Upload")

    if submit:
        if not lecturename.isalnum():
            st.error("Lecturenames must only contain letters and numbers.")
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
                
            