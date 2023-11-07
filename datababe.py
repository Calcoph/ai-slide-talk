import mysql.connector
import streamlit as st
import sys

class Database:
    def __init__(self, database):
        self.mydb = mysql.connector.connect(
            host=st.secrets["mysql_host"],
            #port=st.secrets["mysql_port"],
            user=st.secrets["mysql_user"],
            password=st.secrets["mysql_password"]
        )
        self.__checkDatabaseExists(database)
        self.mydb.database = database #st.secrets["mysql_dbName"]
    
    def query(self, sql_query,data=None):
        cursor = self.mydb.cursor()
        if data != None:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)
        return cursor.fetchall()
    
    def add_user(self, userinfo):
        insert_user_query = """
        INSERT INTO users (email, username, password, openai_api_key)
        VALUES (%s, %s, %s, %s)
        """
        cursor = self.mydb.cursor()
        cursor.execute(insert_user_query,(userinfo["email"],
                                userinfo["username"],
                                userinfo["password"],
                                userinfo["OPENAI_API_KEY"]))
        self.mydb.commit()
    
    def add_history(self, history_entry):
        insert_history_query = """INSERT INTO history (prompt, message, username, lecture, language)
        VALUES (%s, %s, %s, %s, %s)"""
        cursor = self.mydb.cursor()
        cursor.execute(insert_history_query, 
                       (history_entry["prompt"],
                        history_entry["message"],
                        history_entry["username"],
                        history_entry["lecture"],
                        history_entry["language"]))
        self.mydb.commit()
    
    def update_user(self,update_query, userdata):
        cursor = self.mydb.cursor()
        cursor.execute(update_query,userdata)
        self.mydb.commit()

    def add_filestorage(self,file_entry):
        insert_query = "INSERT INTO filestorage (username, lecture, pdf_id, index_faiss_id, index_pkl_id) VALUES (%s, %s, %s, %s, %s)"
        cursor = self.mydb.cursor()
        cursor.execute(insert_query, 
                       (file_entry))
        self.mydb.commit()
    
    def update_filestorage(self,update_query, fileinfos):
        cursor = self.mydb.cursor()
        cursor.execute(update_query,fileinfos)
        self.mydb.commit()
        
    def __checkDatabaseExists(self, database):
        cursor = self.mydb.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [database[0] for database in cursor]
        if not database in databases:
            print(f"Error: database \"{database}\" not found")
            sys.exit(1)

# Usage example
"""
mydb = Database(st.secrets["mysql_dbName"])
result = mydb.query("SHOW DATABASES")
print(result)
databases = [database[0] for database in result]
print(databases)
"""