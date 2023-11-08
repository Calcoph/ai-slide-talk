import openai
import streamlit as st
import pandas as pd
import os, string, random, smtplib
import bcrypt
from cryptography.fernet import Fernet
from history_helpers import load_history
from database import Database

def render_login_register():
    ##

    ## LOGIN
    ##
    login_tab, register_tab = st.tabs(["**Login**", "**Register**"])
    with login_tab:
        with st.form("login", clear_on_submit=False): 
            username = st.text_input("Username")
            password = st.text_input("Password",type="password")  
            login = st.form_submit_button("Login")
        if login:
            login_user(username=username,password=password)
        ##
        ## RESTORE PASSWORD
        ##
        with st.expander("Forgot Password"):
            with st.form("restore_pw",clear_on_submit=True):
                email = st.text_input("Enter your E-Mail")
                restore_pw  = st.form_submit_button("Restore Password")

            if restore_pw:
                with st.spinner("Sending new password."):
                    send_new_password(email)
    ##
    ## REGISTER
    ##    
    with register_tab:
        with st.form("register", clear_on_submit=True):   
            st.subheader("Register")
            email = st.text_input("E-Mail")
            st.warning("Double check your E-Mail-Address, it is the only way to restore your account.")
            username = st.text_input("Username")
            apikey = st.text_input("OPENAI-API KEY",type="password")
            password = st.text_input("Password",type="password")
            register = st.form_submit_button("Register")
        if register:
            salt = bcrypt.gensalt()
            userinfo = {"email": email.lower(),
                        "username":username,
                        "password": bcrypt.hashpw(password=password.encode(),salt=salt),
                        "OPENAI_API_KEY": encrypt_api_key(apikey)
                        }
            with st.spinner("Registering User"):
                create_new_user(userinfo=userinfo,check_key=False)    

#@st.cache_data()
def load_userdb():
    mydb = Database(st.secrets["mysql_dbName"])
    userdb = mydb.query("SELECT * FROM users")
    return pd.DataFrame(userdb,
                        columns=["id","email","username","password","OPENAI_API_KEY"])

def check_api_key(key):
    try:
        openai.api_key = key 
        openai.Completion.create(
        prompt="Test",
        model = "davinci",
            max_tokens=5)
        return True
    except Exception as e:
        #st.write(e)
        return False

def create_new_user(userinfo, check_key=True):
    userdb = load_userdb()
    #check if api key is valid, can be disabled for development purposes, set "check_key" to False
    if not check_api_key(decrypt_api_key(userinfo["OPENAI_API_KEY"])) and check_key:
        st.error("Your OPENAI API-KEY is wrong. Check again.")
        st.stop()        
    # ensure username to be unique
    if userinfo["username"] in list(userdb["username"]):
        st.error("Username already taken. Choose another one.")
        st.stop()
    #add user to database
    db = Database(st.secrets["mysql_dbName"])
    db.add_user(userinfo)
    st.success("You registered succesfully. Login with your credentials.")

def logout_user():
    os.environ["OPENAI_API_KEY"] = ""
    reset_list = ["authentication_status","lecture","language"]
    for item in reset_list:
        st.session_state[item] = False
    st.session_state["username"] = None
    st.rerun()

def login_user(username,password):
    db = Database(st.secrets["mysql_dbName"])
    try:
        userinfo = db.query(f"SELECT * FROM users WHERE username = %s",(username,))[0]
    except IndexError:
        st.warning("Username not correct.")
        return 
    if bcrypt.checkpw(password.encode(),userinfo[3].encode()):
        st.session_state["authentication_status"] = True
        st.session_state["username"] = username
        st.session_state["userhistory"] = load_history()
        os.environ["OPENAI_API_KEY"] = decrypt_api_key(userinfo[4])
        st.rerun()
    else:
        st.error("Password is wrong.")
   

def decrypt_api_key(encrypted_api_key):
    encryption_key = st.secrets["encryption_key"]
    fernet = Fernet(encryption_key)
    return fernet.decrypt(encrypted_api_key).decode()

def encrypt_api_key(raw_api_key):
    encryption_key = st.secrets["encryption_key"]
    fernet = Fernet(encryption_key)
    return fernet.encrypt(raw_api_key.encode())

def send_email(recipient, generated_pw):
    try:
            
        subject = "Your new Slidechatter Password"
        text = f"""
        
        Hey {recipient["username"]},
        
        here is your new slidechatter password, make sure to change it after login in:

        Username: {recipient["username"]}
        New Password: {generated_pw}

        Regards,
        The Slidechatter Team
        """
        message = 'Subject: {}\n{}'.format(subject, text)
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
            smtp_server.login(st.secrets["gmail"], st.secrets["gmail_pw"])
            smtp_server.sendmail(st.secrets["gmail"], recipient["email"], message)
        return True
    except:
        return None

# function from streamlit authenticator (https://github.com/mkhorasani/Streamlit-Authenticator) 
def generate_random_pw(length: int=16) -> str:
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length)).replace(' ','')
 
def send_new_password(email):
    db = Database(st.secrets["mysql_dbName"])
    try:
        userinfo = db.query(f"SELECT * FROM users WHERE email = %s",(email,))[0]
    except IndexError:
        st.error("E-Mail not correct.")
        st.stop()

    recipient = {"email":userinfo[1],
                "username":userinfo[2]}
    
    new_pw = generate_random_pw()
    if send_email(recipient=recipient,generated_pw=new_pw):
        salt = bcrypt.gensalt()
        new_pw_enctrypted = bcrypt.hashpw(password=new_pw.encode(),salt=salt)
        db.update_user("""UPDATE users SET password = %s WHERE username = %s""",(new_pw_enctrypted,st.session_state["username"]))
        st.success("Succesfully send new password.")
        return True
    else:
        print("Error sending new password.")
        return None
    
def change_password(change_info):
    db = Database(st.secrets["mysql_dbName"])
    user_pw = db.query(f"SELECT password FROM users WHERE username = %s",(st.session_state["username"],))[0][0]
    if change_info["newpw1"] != change_info["newpw2"]:
        st.warning("New passwords are not equal.")
        st.stop()
    if bcrypt.checkpw(change_info["oldpw"].encode(),user_pw.encode()):
        salt = bcrypt.gensalt()
        new_pw_encrypted = bcrypt.hashpw(password=change_info["newpw2"].encode(),salt=salt)
        db.update_user("""UPDATE users SET password = %s WHERE username = %s""",(new_pw_encrypted,st.session_state["username"]))
        st.success("Password changed succesfully.")
    else:
        st.warning("Old Password not correct.")
    

def change_openai_apikey(change_info):
    db = Database(st.secrets["mysql_dbName"])
    user_pw = db.query("SELECT password FROM users WHERE username = %s",(st.session_state["username"],))[0][0]
    if bcrypt.checkpw(change_info["oldpw"].encode(),user_pw.encode()):
        if check_api_key(change_info["newapikey"]):
            db.update_user("UPDATE users SET openai_api_key = %s WHERE username = %s",(encrypt_api_key(change_info["newapikey"]),st.session_state["username"]))
            st.success("OPENAI API KEY changed successfully.")
            os.environ["OPENAI_API_KEY"] = change_info["newapikey"]
        else:
            st.warning("New OPENAI API KEY is wrong.")            
    else:
        st.warning("Old Password not correct.")

def check_login(render_login_template=False):
    if st.session_state["authentication_status"]:
        logout = st.sidebar.button("Logout")
        if logout:
            logout_user()
        return True
    else:
        if render_login_template:
            render_login_register()
        else:
            st.warning("Login on the 'ai_slide_talk' page.")
