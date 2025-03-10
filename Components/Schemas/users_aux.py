#Importaciones Externas
from fastapi import status, HTTPException

#Importartaciones Intenas
from DB.client import get_sql_connection
from Components.constants import DATABASE



def json_user (json) -> dict:
    """
    ES: transforma la respuesta Json [list[]], en diccionario
    EN: transforms the Json response [list[]], into a dictionary
    """
    return {
        "id_user":json[0][0],
        "username":json[0][1],
        "rol":json[0][2],
        "disabled":bool(json[0][3]),
        "phone":json[0][4],
        "email":json[0][5],
        "password":json[0][6]
    }


def verification_user (user_dict: dict): 
    """
    ES: Verifica ususario a partit de un diccionario contruido a partir del modelo de Userdb, si
    se encuentra responde la existencia del ususario.
    EN: Verify user from a dictionary built from the Userdb model, if
    the existence of the user is found.
    """
    with get_sql_connection() as connection:
        with connection.cursor() as cursor:
            query = f"SELECT * FROM {DATABASE}.users WHERE email = %s;"
            cursor.execute(query,(user_dict["email"],))
            user = cursor.fetchall()
    if user:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El usuario ya existe"
            )


def captura_user (id_user:int) -> dict:
    """
    ES: Captura los datos a partir de un nombre de usuario, 
    para debolver el ususario requerido en una variable de tipo dict
    EN: Captures data from a username, 
    to return the required user in a dict type variable
    """
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query = f"SELECT * FROM {DATABASE}.users WHERE id_user = %s;"
                cursor.execute(query,(id_user,))
                user = cursor.fetchall()
                user = [list(u)for u in user]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(e)
            )
    return json_user(user)


def existencia(user_dict:dict) -> bool:
    """
    ES: Verifica existencia de usuarios, de ser positiva -> True + ID,
    de ser negativa -> False + None
    EN: Checks the existence of users, if positive -> True + ID,
    if negative -> False + None
    """
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query = f"SELECT * FROM {DATABASE}.users WHERE username = %s;"
                cursor.execute(query,(user_dict["username"],))
                user = cursor.fetchone()
                print(f"funsion: existencia.\nuser encontrado: {user}")
                if user:
                    return True, user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(e)
            )
    return False, None