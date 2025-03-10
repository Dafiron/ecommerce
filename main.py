#Importacion Externa // External Import
from fastapi import FastAPI

#Importacion Interna // Internal Import

from Routers import users
from Routers import login
from Routers import products

#Variables de entorno
from Components.constants import check_environment_variables, list_env_var, is_connected
from dotenv import load_dotenv
load_dotenv()
import os


app = FastAPI(
    title= "Ecommerce Dafiron",
    version="0.1 BETA",
    description= "Api para ecommerce Sencillo",
    docs_url="/docs" if os.getenv("on_dev") == "Y" else None,
    redoc_url="/redoc" if os.getenv("on_dev") == "Y" else None,
    openapi_url="/openapi.json" if os.getenv("on_dev") == "Y" else None,
)

app.include_router(users.router)
app.include_router(login.router)
app.include_router(products.router)

check_environment_variables(list_env_var)

is_connected()

@app.get("/")
async def root():
    return "Api Ecommerce Dafiron: En linea"


