from pydantic import BaseModel

#--------------------------------------- <USER> ---------------------------------------------------------#
# Modelo de ususario sin password
class User(BaseModel):
    """
    ES: clase ususario sin incluir contraseñas.
    EN: user class without including passwords.
    """
    id_user:int | None = None
    username:str
    rol:int = 0
    disabled:bool = False
    phone:str | None = None
    email:str

# Modelo de usuario con password
class Userdb(User):
    """
    ES: Hereda de User agregando password.
    EN: Inherits from User by adding password.
    """
    password:str

#--------------------------------------- < Products > ---------------------------------------------------------#

class Products (BaseModel):
    """
    ES: Clase Codigos, que vertebra los datos subsiguientes.
    EN: Class Codes, which structures the subsequent data.
    """
    id_product : int | None = None
    title: str
    description: str
    price: float = 999999.99
    discount_percentage: float | None = 0.0 
    rating: int | None = None
    brand: str
    category: str
    miniature: str| None = None

# ---------------------------------------- < imagenes > -------------------------------------------- #

class Image (BaseModel):
    id_product: int |None = None
    url: str

