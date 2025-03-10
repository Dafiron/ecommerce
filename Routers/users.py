#importaciones Externas
from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse, Response
from passlib.context import CryptContext

#importaciones Internas
from DB.client import get_sql_connection
from Components.models import User, Userdb
from Components.constants import DATABASE, USERS
from Components.Schemas.users_aux import verification_user, captura_user


router= APIRouter(
    prefix="/users",
    tags=["users"],
    responses={status.HTTP_404_NOT_FOUND:{"message":"No encontrado"}}
    )



# Encriptacion
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# tabla = tabla principal donde se opera.
TABLA = USERS

@router.get("")
async def testigo ():
    return "User listo para el ingreso de datos"



@router.get("/all", status_code=status.HTTP_200_OK)
async def all():
    """
    ES: Solicita todos los datos de la tabla users devolviendo una [List[]].
    EN: it requests all the data from the users table returning a [List[]].
    """
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query = f"SELECT * FROM {DATABASE}.{TABLA};"
                cursor.execute(query)
                result = cursor.fetchall()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
            )
    return result

@router.post("/on", status_code=status.HTTP_201_CREATED,response_model=User)
async def user_on(user:Userdb):
    """
    ES: Crea una entrada en la tabla usuarios a partir del ingreso del modelo Userdb, encriptando el valor de password,
    devuelve un objeto de tipo User.
    EN: Creates an entry in the users table from the Userdb model input, encrypting the password value,
    returns an object of type User.
    """
    user_dict= user.dict()

    #Verificacion de usuario
    verification_user(user_dict)

    #Encriptacion
    user_dict["password"] = crypt.hash(user_dict["password"])
    
    # Elimina el id si lo tuviese por que es un valor UQ en MySQL
    if "id" in user_dict:
        del user_dict["id_user"]
    
    if not "phone" in user_dict or user_dict["phone"] == "":
        user_dict["phone"] = "XXX-XXXXXXX"
    
    user_dict["email"]= str(user_dict["email"]).lower()
    
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query2 = (
                    f"""
                    INSERT INTO {DATABASE}.{TABLA}
                    (username, rol, disabled ,phone , email , password)
                    VALUES (%s, %s, %s, %s, %s, %s);
                    """
                )
                # metodo para evitar inyecciones
                cursor.execute(
                    query2,(
                    user_dict["username"],
                    user_dict["rol"],
                    int(user_dict["disabled"]),
                    user_dict["phone"],
                    user_dict["email"],
                    user_dict["password"],
                    ))
                user_id = cursor.lastrowid
                connection.commit()
                # busca el nuevo ususario para devolverlo como respuesta
                user_dict["id_user"] = user_id
                new_user = captura_user(user_dict["id_user"])
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
            )
    return User(**new_user)


#Put
@router.put("/up",status_code=status.HTTP_200_OK, response_model=User)
async def user_up(user:Userdb):
    """
    ES:Pre: el input debe tener id_user. 
    Actualiza los datos de un Usuario a partir de los datos de usuario,
    EN: Pre: input must have id_user. 
    Updates a User's data from the user data,
    """
    try:
        user_dict = user.dict()
        if not user_dict["id_user"]:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El imput no contiene: 'id_user' sobre el que accionar"
            )
        existencia = captura_user(user_dict["id_user"])
        if existencia:
            user_dict["password"] = crypt.hash(user_dict["password"])
            with get_sql_connection() as connection:
                with connection.cursor() as cursor:
                    query = (
                        f"""
                        UPDATE {DATABASE}.{TABLA}
                        SET username = %s, rol = %s, disabled = %s, email =%s,password = %s
                        WHERE id_user = %s
                        """
                    )
                    # metodo para evitar inyecciones
                    cursor.execute(
                        query,(
                        user_dict["username"],
                        user_dict["rol"],
                        int(user_dict["disabled"]),
                        user_dict["email"],
                        user_dict["password"],
                        user_dict["id_user"]
                        ))
                    connection.commit()
                    # busca el nuevo ususario para devolverlo como respuesta
                    up = captura_user(user_dict["id_user"])
                    if not up:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="discrepacias en los nuevos datos y los viejos."
                        )
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK, 
                content= {"detail":"No se encontro el dato particular"}
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
            )
    return User(**up)


# Delete
@router.delete("/delete/{id}",status_code=status.HTTP_204_NO_CONTENT)
async def user_del(id:int):
    """
    ES: Elimina los datos de un usuario a partir de los datos del modelo Usuario.
    EN: Deletes a user's data from the User model data.
    """
    try:
        user = captura_user(id)
        if user:
            with get_sql_connection() as connection:
                with connection.cursor() as cursor:
                    query = (
                        f"""
                        DELETE FROM {DATABASE}.{TABLA}
                        WHERE id_user = %s;
                        """
                    )
                    cursor.execute(
                        query,(
                        id,
                    ))
                    connection.commit()
                    # busca el nuevo ususario para devolverlo como respuesta
        else:
            return JSONResponse(
                status_code=status.HTTP_200_OK, 
                content= {"detail":"No se encontro el dato particular"}
                )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
            )
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )

