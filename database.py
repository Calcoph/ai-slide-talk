import mysql.connector
from mysql.connector import MySQLConnection
import streamlit as st
import sys

from auth_helpers import UserRegister
from chat_helpers import FullMessage
from typing import Any

from gdrive_helpers import StoredFileData

class Database:
    """
# Usage example
mydb = Database(st.secrets["mysql_dbName"])
result = mydb.query("SHOW DATABASES")
print(result)
databases = [database[0] for database in result]
print(databases)
"""

    def __init__(self):
        self.mydb: MySQLConnection = mysql.connector.connect(
            host=st.secrets["my_sql"]["mysql_host"],
            #port=st.secrets["mysql_port"],
            user=st.secrets["my_sql"]["mysql_user"],
            password=st.secrets["my_sql"]["mysql_password"]
        )
        self.__checkDatabaseExists(st.secrets["my_sql"]["mysql_dbName"])
        self.mydb.database = st.secrets["my_sql"]["mysql_dbName"] #st.secrets["mysql_dbName"]

    def query(self, sql_query,data=None):
        cursor = self.mydb.cursor()
        if data != None:
            cursor.execute(sql_query, data)
        else:
            cursor.execute(sql_query)
        return cursor.fetchall()

    def add_user(self, userinfo: UserRegister):
        insert_user_query = """
        INSERT INTO users (email, username, password, openai_api_key)
        VALUES (%s, %s, %s, %s)
        """
        cursor = self.mydb.cursor()
        cursor.execute(insert_user_query,(userinfo.email,
                                userinfo.username,
                                userinfo.password,
                                userinfo.open_api_key))
        self.mydb.commit()

    def add_history(self, history_entry: FullMessage):
        """Add a message to the history"""

        insert_history_query = """
        INSERT INTO history (prompt, message, username, lecture, language)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor = self.mydb.cursor()
        cursor.execute(insert_history_query,
                       (history_entry.prompt,
                        history_entry.message,
                        history_entry.username,
                        history_entry.lecture,
                        history_entry.language))
        self.mydb.commit()

    def execute_query(self, query: str, data: tuple[Any]):
        """Execute any sql query

        Args:
            query (str): template query
            data (tuple[Any]): query arguments
        """

        cursor = self.mydb.cursor()
        cursor.execute(query, data)
        self.mydb.commit()

    def add_filestorage(self, file_entry: StoredFileData):
        """Store a google drive's file metadata for later retrieval"""

        insert_query = """
        INSERT INTO filestorage (username, lecture, pdf_id, index_faiss_id, index_pkl_id)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor = self.mydb.cursor()
        cursor.execute(
            insert_query,
            (
                file_entry.username,
                file_entry.lecture,
                file_entry.pdf_id,
                file_entry.index_faiss_id,
                file_entry.index_pkl_id
            )
        )
        self.mydb.commit()

    def __checkDatabaseExists(self, database: str):
        cursor = self.mydb.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [database[0] for database in cursor]
        if not database in databases:
            print(f"Warning: database \"{database}\" not found")
            print(f"Creating database \"{database}\"...")
            self.create_database()

    def create_database(self):
        cnx =  mysql.connector.connect(host="localhost",
                                    user=st.secrets["my_sql"]["mysql_user"],
                                password=st.secrets["my_sql"]["mysql_password"])
        create_db_query = f"CREATE DATABASE {st.secrets['my_sql']['mysql_dbName']}"
        with cnx.cursor() as cursor:
            try:
                cursor.execute(create_db_query)
            except:
                pass
        create_users_table_query = """CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        openai_api_key VARCHAR(255) NOT NULL
        )
        """
        # Create the 'history' table
        create_history_table_query = """
        CREATE TABLE IF NOT EXISTS history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            prompt TEXT NOT NULL,
            message TEXT NOT NULL,
            username VARCHAR(255) NOT NULL,
            lecture VARCHAR(255),
            language VARCHAR(255)
        )
        """

        create_filestorage_table_query = """
        CREATE TABLE IF NOT EXISTS filestorage (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            lecture VARCHAR(255) NOT NULL,
            pdf_id VARCHAR(255) NOT NULL,
            index_faiss_id VARCHAR(255) NOT NULL,
            index_pkl_id VARCHAR(255) NOT NULL
        )
        """
        mydb = Database()
        mydb.query(create_history_table_query)
        mydb.query(create_users_table_query)
        mydb.query(create_filestorage_table_query)
