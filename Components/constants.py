from DB.client import get_sql_connection
from dotenv import load_dotenv
import os

load_dotenv()

# Tablas
DATABASE = os.getenv("db_sql_database")
IMAGES = os.getenv("images")
PRODUCTS = os.getenv("products")
USERS = os.getenv("users")

# Palabra secreta 
secret =os.getenv("SECRET")

# Tipo de logaridmo
ALGORITHM = "HS256"


roles= {
    0:"client",
    1:"sellers"
}

MAX_FILES_ALLOWED = 7

#S3
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
REGION=os.getenv("REGION")
CLOUDFRONT_DOMAIN = os.getenv("CLOUDFRONT_DOMAIN")

list_env_var=[
    "db_sql_database","db_sql_host", "db_sql_user","SECRET","on_dev","db_sql_password","products",
    "images", "users","AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY","REGION", "CLOUDFRONT_DOMAIN"
    ]

ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif"]

def check_environment_variables(required_vars: list):
    """
    Verifica si las variables de entorno requeridas están definidas.
    :param required_vars: Lista de nombres de las variables de entorno requeridas.
    """
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Faltan las siguientes variables de entorno: {', '.join(missing_vars)}"
        )
    print("*---Todas las variables de entorno están definidas correctamente.---*")

def is_connected():
    try:
        connection = get_sql_connection()
        print("Conexión exitosa a la base de datos.")
        connection.close()
    except Exception as e:
        print(f"Error al conectar a la base de datos: {e}")

