#Importacion Externa // External Import
from fastapi import status, Depends, HTTPException
from jwt import decode, ExpiredSignatureError, InvalidTokenError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from json import loads

#Importacion Interna // Internal Import
from Components.models import User
from Components.Schemas.users_aux import captura_user
from Components.constants import ALGORITHM, secret


# Sistema de Autorización 
oauth2 = OAuth2PasswordBearer(tokenUrl="login")

# Encriptacion
crypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

#------------------------------------------------------------------------#
# Funsion asyncrona que depende de la Autorizacion del oauth2 
# un token tiene todos los datos nesesarios para validad el cliente
# el token en este caso es de tipo Bearer

async def auth_user(token: str = Depends(oauth2)):
    """
    ES: Utilizando el token (provisto por el usuario) + la palabra secreta + el algorithmo, para Autorizar o no.
    EN: Using the token (provided by the user) + the secret word + the algorithm, to Authorize or not.
    """
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No Autorizado",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        # Decodifica el token
        payload = decode(token, key=secret, algorithms=[ALGORITHM])
        sub = payload.get("sub")
        sub = loads(sub)
        if not sub:
            raise exception

        # Extrae el id_user del campo "sub"
        id_user = sub.get("id_user")
        if not id_user:
            raise exception
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ha expirado")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token inválido o malformado")

    # Busca al usuario en la base de datos usando el id_user
    user_db = captura_user(id_user)
    if not user_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )

    # Convierte el diccionario a un objeto User
    return User(**user_db)

# Verifica si el usuario esta inactivo
async def current_user(user: User = Depends(auth_user)):
    """
    ES: Función que determina si el usuario esta inactivo mediante el valor de disabled.
    EN: Function that determines if the user is inactive using the value of disabled.
    """
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario está inactivo. Por favor, contacte al administrador."
        )
    return user