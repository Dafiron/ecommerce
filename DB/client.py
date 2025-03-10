from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

sql_pass = os.getenv("db_sql_password")
sql_user = os.getenv("db_sql_user")
sql_host = os.getenv("db_sql_host")
sql_port = os.getenv("db_sql_port")
sql_database = os.getenv("db_sql_database")

def get_sql_connection():
    config = {
        "host": sql_host,
        "port": int(sql_port),
        "database": sql_database,
        "user": sql_user,
        "password": sql_pass,
        "connect_timeout": 10,
        "use_pure": True  # Solo necesario si hay problemas con caching_sha2_password
    }
    try:
        connection = mysql.connector.connect(**config)
        return connection
    except mysql.connector.Error as err:
        if err.errno == mysql.connector.errorcode.ER_ACCESS_DENIED_ERROR:
            print("Error: Usuario o contraseña incorrectos.")
        elif err.errno == mysql.connector.errorcode.ER_BAD_DB_ERROR:
            print("Error: La base de datos no existe.")
        else:
            print(f"Error inesperado: {err}")
        raise