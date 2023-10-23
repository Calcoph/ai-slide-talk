import mysql.connector
import streamlit as st
import sys

class Database:
    def __init__(self, database):
        self.mydb = mysql.connector.connect(
            host=st.secrets["mysql_host"],
            user=st.secrets["mysql_user"],
            password=st.secrets["mysql_password"]
        )
        self.__checkDatabaseExists(database)
        self.mydb.database = database #st.secrets["mysql_dbName"]
    
    def query(self, sql_query):
        cursor = self.mydb.cursor()
        cursor.execute(sql_query)
        return cursor.fetchall()
    
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