#Importacion Externa // External Import
from fastapi import APIRouter, status, Depends, HTTPException
from jwt import encode
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
import json


#Importacion Interna // Internal Import
from Components.models import User
from Components.Schemas.users_aux import existencia, json_user
from Components.Schemas.auth_aux import current_user
from Components.constants import roles, ALGORITHM, secret


router= APIRouter(
    prefix="/login",
    tags=["login"],
    responses={status.HTTP_404_NOT_FOUND:{"message":"No encontrado"}}
    )



# Duracion del token en minutos
ACCESS_TOKEN_DURATION = 480

# Sistema de Autorización 
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Encriptacion
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.get("")
async def testigo ():
    return "Login listo para el ingreso de datos"

#------------------------------------------ < Inicio > ------------------------------------------------------------#

@router.post("/")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    """
    ES: Llamada que con un form que se compone de username y password, y luego de verificar, y discriminar el rol,
    devuelve un token:
    {"access_token": "XXXX","token_type":"XXXX", "rol": ["XXXX"]}
    EN: Call with a form that is made up of username and password, and after verifying and discriminating the role,
    returns a token:
    {"access_token": "XXXX","token_type":"XXXX", "role": ["XXXX"]}
    """
    try:
        u = {"username":form.username}
        barrera, found = existencia(u)
        if not barrera:
            raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El usuario no es correto"
            )
        us=[]
        us.append(list(found))
        found = us
        user_dict = json_user(found)

        # Se encontro pero al verificar el pasword no coincide, Exception 
        if not crypt.verify(form.password, user_dict.get("password")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="La contraseña no es correta"
            )
        if user_dict["rol"] in roles:
            user_dict["rol"] = roles[user_dict["rol"]]
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="No se encontro rol asosiado "
            )
        access_token = {
            #se utiliza la biblioteca json para pasar de un objeto de tipo json a un str, puesto que la decodificacion en un formato != str no es posible; con la biblioteca en uso.
            "sub":json.dumps({"username":user_dict.get("username"), "email": user_dict["email"], "id_user": user_dict["id_user"]}),
            "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)
        }
    except HTTPException as e:
        # Relanzar excepciones HTTP específicas sin alterarlas
        raise e
    except Exception as e:
        # Manejar cualquier otro error inesperado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    print(f"secreto: {secret}, algoritmo: {ALGORITHM}")
    return {"access_token": encode(access_token,key=secret,algorithm=ALGORITHM ),"token_type":"bearer", "rol": user_dict["rol"]}

# endpoint para verificar el token
@router.get("/verify-token")
async def verify_token(user: User = Depends(current_user)):
    """
    ES: Endpoint que verifica validez de token, de tipo 'Bearer Token'.
    EN: Endpoint that verifies token validity, of type 'Bearer Token'.
    """
    return {
        "message": "Token is valid",
        "user": {
            "username": user.username,
            "email": user.email,
            "id_user": user.id_user,
            "rol": user.rol
        }
    }
