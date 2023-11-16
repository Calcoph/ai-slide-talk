import streamlit as st
from auth_helpers import check_login
from initialize import load_lecturenames
import base64
from gdrive_helpers import download_pdf

st.set_page_config(
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="documentation\SlideChatter.ico"
)

# def displayPDF(file):
#     # Opening file from file path
#     with open(file, "rb") as f:
#         base64_pdf = base64.b64encode(f.read()).decode('utf-8')

#     # Embedding PDF in HTML
#     pdf_display = F'<embed src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf">'
#     # Displaying File
#     st.markdown(pdf_display, unsafe_allow_html=True)

if check_login():

    st.title("PDF Viewer")
    load_lecturenames()
    with st.form(key="lecture_submit"):
          lecture = st.selectbox("Select the lecture you want to display.", options=st.session_state["lecture_list"])
          lecture_submit = st.form_submit_button("Download from Server")
    if lecture_submit:
        download_pdf(st.session_state["username"],lecture)
        with open(f"tmp/{lecture}/{lecture}.pdf", "rb") as fp:
                    pdf_file = fp.read()
        download = st.download_button("Start Download",pdf_file,f"{lecture}.pdf")



    # with st.form(key="lecture_submit"):
    #     lecture = st.selectbox("Select the lecture you want to display.", options=st.session_state["lecture_list"])
    #     lecture_submit = st.form_submit_button("Show PDF")
    # if lecture_submit:
    #     with st.spinner("Downloading"):
    #         download_pdf(st.session_state["username"],lecture)
    #         #displayPDF(f"tmp/{lecture}/{lecture}.pdf")
    #         with open(f"tmp/{lecture}/{lecture}.pdf", "rb") as fp:
    #             pdf_file = fp.read()
            


