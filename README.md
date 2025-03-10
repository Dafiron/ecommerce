## Ecommerce API

## Índice / Table of Contents

### Español (ES)
1. [Descripción](#descripción)
2. [Tecnologías](#tecnologías--technologies)
3. [Bases de Datos](#bases-de-datos)
   - [Esquema](#schema)
   - [Tabla `users`](#tabla-users)
   - [Tabla `products`](#tabla-products)
   - [Tabla `images`](#tabla-images)
4. [Documentación Específica](#documentación-específica)
5. [Endpoints / Modelos](#endpoints--modelos)
   - [USER](#user)
   - [LOGIN](#login)
   - [PRODUCTS](#products)
6. [Variables de Entorno](#variables-de-entorno)
7. [Ejecución](#ejecucion)
8. [Licencias](#licencias)

### English (EN)
1. [Description](#description)
2. [Technologies](#technologies--technologies)
3. [Database](#database)
   - [Schema](#schema)
   - [`users` Table](#users-table)
   - [`products` Table](#products-table)
   - [`images` Table](#images-table)
4. [Specific Documentation](#specific-documentation--documentación-específica)
5. [Endpoints / Models](#endpoints--models)
   - [USER](#user)
   - [LOGIN](#login)
   - [PRODUCTS](#products)
6. [Environment Variables](#environment-variables)
7. [Execution](#execution)
8. [Licenses](#licenses)


## ES (Español)
### Descripción
API para gestionar un ecommerce simple. Permite crear, actualizar y eliminar productos, usuarios e imágenes, con autenticación JWT y almacenamiento en AWS S3.

Su desarrollo fue en el lenguaje Python, bajo la tecnologia de Fastapi, se opto por una base de datos Relacional, y un servicio de almacenamiento de imagenes y servido de las mismas, para su posterior uso.

### Tecnologías / Technologies
- **Backend**: FastAPI (Python)
- **Base de Datos**: MySQL
- **Almacenamiento de Imágenes**: AWS S3 + CloudFront
- **Autenticación**: JWT (OAuth2)

### Bases de Datos

[Descargar PDF](schema.pdf)

La Base de Datos fue confeccionada en MySQL, simplemente se opto por una plataforma relacional por su masividad de uso y popularidad.

Para el almacenaje de las imagenes y su despliegue se utilizo los servicios de AWS S3, debido a su popularidad y sobre todo a su posto (gratis).

#### SCHEMA

#### Tabla `users`


| Columna       | Tipo         | Descripción / Description                          |
|---------------|--------------|----------------------------------------------------|
| id_user       | INT          | PK, NN, AI (Primary Key, Not Null, Auto Increment) |
| username      | VARCHAR(80)  | NN, UQ (Not Null, Unique)                          |
| rol           | INT          | NN (0: Cliente, 1: Vendedor)                       |
| disabled      | BOOLEAN      | NN (default: False)                                |
| phone         | VARCHAR(45)  | NN (default: "XXX-XXXXXXX")                        |
| email         | VARCHAR(80)  | NN, UQ                                             |
| password      | VARCHAR(120) | NN (hashed con bcrypt)                             |

#### Tabla `products`

| Columna             | Tipo         | Descripción / Description               |
|---------------------|--------------|-----------------------------------------|
| id_product          | INT          | PK, NN, AI                              |
| title               | VARCHAR(100) | NN                                      |
| description         | VARCHAR(200) | NN                                      |
| price               | FLOAT        | NN                                      |
| discount_percentage | FLOAT        | default: 0                              |
| rating              | INT          | nullable                                |
| brand               | VARCHAR(40)  | NN                                      |
| category            | VARCHAR(60)  | NN                                      |
| miniature           | VARCHAR(150) | nullable (URL de la miniatura en S3)    |

#### Tabla `images`

| Columna     | Tipo         | Descripción / Description               |
|-------------|--------------|-----------------------------------------|
| id_image    | INT          | PK, NN, AI                              |
| id_product  | INT          | FK (products.id_product)                |
| image_url   | VARCHAR(150) | NN (URL de la imagen en S3)             |


### Documentación Específica

Fastapi en su uso y coperacion con la tecnologia de Swagger UI nos facilita una documentación resumida y ordenada en {url_de_despliegue}/docs
o la opccion de ReDoc {url_de_despliegue}/redoc

### Endpoints / Modelos
### USER

##### Modelos

###### User
clase ususario sin incluir contraseñas

id_user (integer | null)
username string
rol integer
disabled boolean
phone (string | null)
email string

###### Userdb
Hereda de User agregando password

id_user (integer | null)
username string
rol integer
disabled boolean
phone (string | null)
email string
password string

#### Endpoint

#### **/users/all** (GET)
- **Descripción:** Solicita todos los datos de la tabla users devolviendo una [List[]].
- **Responses:**
    - **200 OK:**
[
  [
    id_user,
    username,
    rol,
    disabled,
    phone,
    email,
    password
  ],
  [
    ...
  ]
]

#### **/users/on** (POST)
- **Descripción:** Crea una entrada en la tabla usuarios a partir del ingreso del modelo Userdb, encriptando el valor de password, devuelve un objeto de tipo User.

- **Request Body:**
  ```json
    {
    "id_user": 0,
    "username": "string",
    "rol": 0,
    "disabled": false,
    "phone": "string",
    "email": "string",
    "password": "string"
    }

- **Responses:**
    - **201 Created:**
    {
    "id_user": 0,
    "username": "string",
    "rol": 0,
    "disabled": false,
    "phone": "string",
    "email": "string"
    }

    - **404 Not Found:**
    "string"

    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/users/up** (PUT)
- **Descripción:** Pre: el input debe tener id_user. Actualiza los datos de un Usuario a partir de los datos del modelo Usuario.
- **Request Body:**
  ```json
    {
    "id_user": 0,
    "username": "string",
    "rol": 0,
    "disabled": false,
    "phone": "string",
    "email": "string",
    "password": "string"
    }

- **Responses:**
    - **200 OK:**
    {
    "id_user": 0,
    "username": "string",
    "rol": 0,
    "disabled": false,
    "phone": "string",
    "email": "string"
    }

    - **404 Not Found:**
    "string"

    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/users/delete/{id}** (DELET)
- **Descripción:** Elimina los datos de un usuariosera por el username.
- **Parameters:**
id : integer (path)

- **Responses:**
    - **204 No Content:**
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

### LOGIN

#### **/login/** (POST)
- **Descripción:** Llamada que con un form que se compone de username y password, y luego de verificar, y discriminar el rol, devuelve un token: {"access_token": "XXXX","token_type":"XXXX", "rol": ["XXXX"]}
- **Request Body:**
    grant_type: string
    username: string (requerido)
    password: string (requerido)
    scope: string
    client_id: string
    client_secret: string

- **Responses:**
    - **200 OK:**
    {"access_token": "XXXX","token_type":"XXXX", "rol": ["XXXX"]}
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### /login/verify-token (GET)
- **Descripción:** Verifica el token de autenticación.
- **Responses:**
    - **200 OK:**
    {"message": "Token is valid",
        "user": {
            "username": str,
            "email": str,
            "id_user": int,
            "rol": int 
        }
    }
    - **404 Not Found:**
    "string"

### PRODUCTS

#### MODELOS

##### Products

id_product (integer | null)
title string
description string
price number
discount_percentage (number | null)
rating (integer | null)
brand string
category string
miniature (string | null)

##### Image
id_product (integer | null)
url string


#### **/products/upload-image/{id_product}** (POST)
- **Descripción:** Establece, el nombre del archivo a travez de la consulta si existen otras imagenes vinculadas al id_products -> Sube el archivo renombrado a aws (dentro de este a la carpeta nombrada 'images/'), para servirlo -> Retornado una leyenda y la url
- **Parameters:**
id_product : integer (path)

- **Request Body:**  multipart/form-data
image : string($binary)

- **Responses:**
    - **201 Created:**
    {"message": "Imágen subida exitosamente", "urls": "XXXX"}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/image/{id_product}/on** (POST)
- **Descripción:** Pre: El producto es valido y existe en Base de datos. Agrega una imagen al producto previamente creado. subiendo y sirviendolo en AWS S3; Luego se hacen las inyecciones en base de datos pertinentes.

- **Parameters:**
id_product : integer (path)

- **Request Body:**  multipart/form-data
images : array (string)

- **Responses:**
    - **201 Created:**
    {"message": "Imágenes subidas exitosamente", "urls": "XXXX"}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/create** (POST)
- **Descripción:** Creacion de producto, con el modelo Products. Si se provee id_porducts, NO se toma en consideracion. Respuesta afirmativa a la creación 201 -> {"message": str, "product": Products }

- **Request Body:**
  ```json
    {
    "id_product": 0,
    "title": "string",
    "description": "string",
    "price": 999999.99,
    "discount_percentage": 0,
    "rating": 0,
    "brand": "string",
    "category": "string",
    "miniature": "string"
    }

- **Responses:**
    - **201 Created:**
    {"message": "Producto creado exitosamente", "product": Products(MODEL)}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/upload-miniature/{id_product}** (POST)
- **Descripción:** Establece, el nombre del archivo 'product_'+(ultimo id_product +1) v Sube el archivo renombrado a aws (dentro de la carpeta:'miniatures/'), para servirlo v Retornado una leyenda y la url

- **Parameters:**
id_product : (integer | null) (path)

- **Request Body:**   multipart/form-data
miniature : string($binary)

- **Responses:**
    - **201 Created:**
    {"message": "Miniatura subida correctamente", "url": "xxxx"} ("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/on** (POST)
- **Descripción:** Creación de producto con datos con base al modelo Product, un json, converso a str y miniatura opcional.

- **Request Body:**  multipart/form-data

product_data: string 

Ejemplo:
curl -X POST "http://localhost:8000/products/on" \
-H "Content-Type: multipart/form-data" \
-F "product_data={\"title\": \"Test\", \"price\": 99.99}" \
-F "miniature=@test.jpg"

miniature : string($binary)

- **Responses:**
    - **201 Created:**
    {"message": "Miniatura Subida y producto creado exitosamente", "product": Products(MODEL), "url":"xxxx"}("string")

    - **201 Created:**
    {"message": "Producto creado exitosamente", "product": Products(MODEL)}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/delete/{id_product}** (DELET)
- **Descripción:** Elimina un producto, si este tiene imagenes vinculadas en AWS S3, tambien se prosede a su eliminacion.

- **Parameters:**
id_product : integer (path)

- **Responses:**
    - **204 No Content:**
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/image/{id_image}/delete** (DELET)
- **Descripción:**  Elimina la imagen de Base de datos; sí esta esta alojada en AWS, tambien se prosede a su eliminacion.

- **Parameters:**
id_image : integer (path)

- **Responses:**
    - **204 No Content:**
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/delete-image/** (DELET)
- **Descripción:**  Detecta Pertenencia del url en base al dominio, de ser propietario, prosede a su eliminacion.

- **Request Body:**
  ```json
    {
    "id_product": 0,
    "url": "string"
    }

- **Responses:**
    - **204 No Content:**
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/update** (PUT)

- **Descripción:** Pre: el cuerpo incluye el id_product. Actualiza las columnas resferentes a un producto en la tabla product.
- **Request Body:** 
  ```json
    {
    "id_product": 0,
    "title": "string",
    "description": "string",
    "price": 999999.99,
    "discount_percentage": 0,
    "rating": 0,
    "brand": "string",
    "category": "string",
    "miniature": "string"
    }

- **Responses:**
    - **200 OK:**
    {"message": "Producto Actualizado correctamente", "product": Products(MODEL)}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/up** (PUT)

- **Descripción:** Pre: el cuerpo incluye el id_product; si se busca modificar la miniatura ademas de las columnas de la tabla, miniatura debe ser None(o quivalente) Actualiza tanto las comuna de la tabla product en lo referente a un producto como a su miniatura asociada (si la ubiese). dado que form solo hacepta tanto datos file como text: 'product_data' es un constructo json comberso a str. si se provee un url distiento del que se tiene en base de datos y un archivo file para la miniatura prima simpre el file descartando el url provisto. 

- **Request Body:**  multipart/form-data

product_data: string 

Ejemplo:
"product_data={\"title\": \"Test\", \"price\": 99.99}" \ ...

miniature : string($binary)

- **Responses:**
    - **200 OK:**
    {"message": "Producto Actualizado correctamente", "product": Products(MODEL)}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/all** (GET)
- **Descripción:** Restona todos productos y sus imagenes vinculadas.
- **Responses:**
    - **200 OK:**
{"message": "Exito en el proseso", "products":[
    {
    "id_product": int,
    "title":str,
    "description":str,
    "price":float,
    "discountPercentage":float,
    "rating":int,
    "brand":str,
    "category":str,
    "miniature":str,
    "images":[str,str]
    },{}]
}

#### **/products/category/{category}** (GET)
- **Descripción:**
- **Parameters:**
category : string (path)

- **Responses:**
    - **200 OK:**
{"message": "Exito en el proseso", "products":[
    {
    "id_product": int,
    "title":str,
    "description":str,
    "price":float,
    "discountPercentage":float,
    "rating":int,
    "brand":str,
    "category":str,
    "miniature":str,
    "images":[str,str]
    },{}]
}
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }


### Variables de Entorno
Crea un archivo `.env` con:
    ```env
    db_sql_database={NOMBRE_DE_LA_DATABASE}
    db_sql_host={HOST}
    db_sql_port={PUERTO}
    db_sql_password={CONTRASEÑA}
    db_sql_user={USUARIO}

    on_dev="Y" (O "N" EN CASO DE ESTAR EN PRODUCCION)

    SECRET={PALABRA_SECRETA}

    products="products"
    images="images"
    users="users"

    AWS_ACCESS_KEY_ID ="HGTGTYSTYHJJDMNCVB" (EJEMPLO)
    AWS_SECRET_ACCESS_KEY="FEGUHIFEGUFAGMdfiufgJFDBFG564/AGFD" (EJEMPLO)
    REGION="us-east-2"(LA REGION ASIGNADA POR AWS)
    CLOUDFRONT_DOMAIN ="https://abc123.cloudfront.net" (EJEMPLO)


### Ejecucion

#### Entorno Local

1. Se recomienda ejecutar el proyecto en un entorno virtual para evitar conflictos con otras dependencias del sistema.

Si no tienes un entorno virtual configurado, puedes crearlo y activarlo con los siguientes comandos:
Crear un entorno virtual (si no lo tienes)
    python -m venv venv

Activar el entorno virtual
En Windows:
    venv\Scripts\activate

En Linux/Mac:
    source venv/bin/activate

elemplo en termial:
{ubicado en raiz del proyecto}>python -m venv venv
{ubicado en raiz del proyecto}>venv\Scripts\activate
(venv) {ubicado en raiz del proyecto}>

2. Instalación de dependencias:
    pip install -r requirements.txt

3. Inicio del servidor

comando de inicio del servidor:

{ubicado en raiz del proyecto}> uvicorn main:app --host 0.0.0.0 --port 8000 --reload


El archivo main.py contiene dos funciones importantes que verifican el entorno antes de iniciar el servidor:

4. Verificación del entorno
check_environment_variables()
    verifica que todas las variables de entorno esten correctamente definidas:
        - respuesta positiva: *---Todas las variables de entorno están definidas correctamente.---*
        - respuesta negativa: Faltan las siguientes variables de entorno: XXX, ZZZ, YYY

5. Verifica la conexión a la base de datos
is_connected()
    verifica la conexion a base de datos (en este caso mysql) 
        - respuesta positiva: Conexión exitosa a la base de datos
        - respuesta negativa: Error al conectar a la base de datos:{error espesifico} 


6. Ejemplo de salida en la terminal
ejemplo de vision en terminal:
INFO:     Will watch for changes in these directories: ['{ubicado en raiz del proyecto}']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [14632] using WatchFiles
*---Todas las variables de entorno están definidas correctamente.---* 
Conexión exitosa a la base de datos.
INFO:     Started server process [14040]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

Una vez que el servidor esté en funcionamiento, puedes acceder a la API en tu navegador o mediante herramientas como curl o Postman o Thunder Client:

URL base: http://localhost:8000

y si la variable de entorno 'on_dev' == "Y":

Documentación interactiva (Swagger UI): http://localhost:8000/docs 

Documentación alternativa (ReDoc): http://localhost:8000/redoc

De lo contrario, es decir: 'on_dev' != "Y"

no sera visible; esto es espacialmente util para el despliegue del proyecto.

7. Cierre

Para cerrar el servidor: presione CTRL+C

y el entorno virtual: en la terminal que este sindo ejecutado: (venv) {ubicado en raiz del proyecto}> deactivate


#### Archivo Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT

### Licencias
- **Este proyecto**: MIT License (ver [LICENSE](LICENSE)).
- **Dependencias**: Ver [LICENSES.md](LICENSES.md).
- **Nota**: `mysql-connector-python` está bajo GPL. Si usas este código en producción, considera migrar a `pymysql` (MIT License).


## EN (English)
### Database
[Download PDF](schema.pdf)

The database was built with **MySQL**, chosen for its widespread use and popularity.  
For image storage and delivery, **AWS S3** was used due to its popularity and free tier benefits.

#### Schema

##### `users` Table
| Column       | Type         | Description                                        |
|--------------|--------------|----------------------------------------------------|
| id_user      | INT          | PK, NN, AI (Primary Key, Not Null, Auto Increment) |
| username     | VARCHAR(80)  | NN, UQ (Not Null, Unique)                          |
| rol          | INT          | NN (0: Customer, 1: Seller)                        |
| disabled     | BOOLEAN      | NN (default: False)                                |
| phone        | VARCHAR(45)  | NN (default: "XXX-XXXXXXX")                        |
| email        | VARCHAR(80)  | NN, UQ (Not Null, Unique)                          |
| password     | VARCHAR(120) | NN (hashed with bcrypt)                            |

##### `products` Table
| Column             | Type         | Description                           |
|---------------------|--------------|--------------------------------------|
| id_product         | INT          | PK, NN, AI                            |
| title              | VARCHAR(100) | NN                                    |
| description        | VARCHAR(200) | NN                                    |
| price              | FLOAT        | NN                                    |
| discount_percentage| FLOAT        | default: 0                            |
| rating             | INT          | nullable                              |
| brand              | VARCHAR(40)  | NN                                    |
| category           | VARCHAR(60)  | NN                                    |
| miniature          | VARCHAR(150) | nullable (Thumbnail URL in S3)        |

##### `images` Table
| Column      | Type         | Description                          |
|-------------|--------------|--------------------------------------|
| id_image    | INT          | PK, NN, AI                           |
| id_product  | INT          | FK (products.id_product)             |
| image_url   | VARCHAR(150) | NN (Image URL in S3)                 |


### Specific Documentation / Documentación Específica

**FastAPI**, in its integration with **Swagger UI**, provides concise and organized documentation at `{url_de_despliegue}/docs`  
or the **ReDoc** option at `{url_de_despliegue}/redoc`.

---

### Endpoints / Models

#### USER

##### Models

###### User
User class without password fields.

- `id_user` (integer | null)
- `username` string
- `rol` integer
- `disabled` boolean
- `phone` (string | null)
- `email` string

###### Userdb
Inherits from `User`, adding the `password` field.

- `id_user` (integer | null)
- `username` string
- `rol` integer
- `disabled` boolean
- `phone` (string | null)
- `email` string
- `password` string

---

#### Endpoints

#### **/users/all** (GET)
- **Description:** Retrieves all data from the `users` table as a list.
- **Responses:**
  - **200 OK:**  
    ```json
    [
      [id_user, username, rol, disabled, phone, email, password],
      [...]
    ]
    ```

#### **/users/on** (POST)
- **Description:** Creates a user entry in the database using the `Userdb` model, encrypting the password. Returns a `User` object.

- **Request Body:**
  ```json
    {
    "id_user": 0,
    "username": "string",
    "rol": 0,
    "disabled": false,
    "phone": "string",
    "email": "string",
    "password": "string"
    }

- **Responses:**
    - **201 Created:**
    {
    "id_user": 0,
    "username": "string",
    "rol": 0,
    "disabled": false,
    "phone": "string",
    "email": "string"
    }

    - **404 Not Found:**
    "string"

    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/users/up** (PUT)
- **Descripción:** Pre: input must have id_user. Updates data for a User from data in the User model.
- **Request Body:**
  ```json
    {
    "id_user": 0,
    "username": "string",
    "rol": 0,
    "disabled": false,
    "phone": "string",
    "email": "string",
    "password": "string"
    }

- **Responses:**
    - **200 OK:**
    {
    "id_user": 0,
    "username": "string",
    "rol": 0,
    "disabled": false,
    "phone": "string",
    "email": "string"
    }

    - **404 Not Found:**
    "string"

    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/users/delete/{id}** (DELET)
- **Descripción:** Delete a user's data
- **Parameters:**
id : integer (path)

- **Responses:**
    - **204 No Content:**
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

### LOGIN

#### **/login/** (POST)
- **Descripción:** Call that with a form consisting of username and password, and after verifying and discriminating the role, returns a token: {"access_token": "XXXX","token_type":"XXXX", "rol": ["XXXX"]}

- **Request Body:**
    grant_type: string
    username: string (requerido)
    password: string (requerido)
    scope: string
    client_id: string
    client_secret: string

- **Responses:**
    - **200 OK:**
    {"access_token": "XXXX","token_type":"XXXX", "rol": ["XXXX"]}
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### /login/verify-token (GET)
- **Descripción:** Verify the authentication token.
- **Responses:**
    - **200 OK:**
    {"message": "Token is valid",
        "user": {
            "username": str,
            "email": str,
            "id_user": int,
            "rol": int 
        }
    }
    - **404 Not Found:**
    "string"

### PRODUCTS

#### MODELS

##### Products

id_product (integer | null)
title string
description string
price number
discount_percentage (number | null)
rating (integer | null)
brand string
category string
miniature (string | null)

##### Image
id_product (integer | null)
url string


#### **/products/upload-image/{id_product}** (POST)
- **Descripción:** Set the file name through the query if there are other images linked to the id_products -> Upload the renamed file to aws (within this to the folder named 'images/'), to serve it -> Returns a legend and the url
- **Parameters:**
id_product : integer (path)

- **Request Body:**  multipart/form-data
image : string($binary)

- **Responses:**
    - **201 Created:**
    {"message": "Imágen subida exitosamente", "urls": "XXXX"}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/image/{id_product}/on** (POST)
- **Descripción:** Pre: The product is valid and exists in the database. Add an image to the previously created product, uploading and serving it to AWS S3; then perform the relevant database injections.

- **Parameters:**
id_product : integer (path)

- **Request Body:**  multipart/form-data
images : array (string)

- **Responses:**
    - **201 Created:**
    {"message": "Imágenes subidas exitosamente", "urls": "XXXX"}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/create** (POST)
- **Descripción:** Product creation, with the Products model. If id_porducts is provided, it is NOT taken into consideration. Affirmative response to creation 201 -> {"message": str, "product": Products }

- **Request Body:**
  ```json
    {
    "id_product": 0,
    "title": "string",
    "description": "string",
    "price": 999999.99,
    "discount_percentage": 0,
    "rating": 0,
    "brand": "string",
    "category": "string",
    "miniature": "string"
    }

- **Responses:**
    - **201 Created:**
    {"message": "Producto creado exitosamente", "product": Products(MODEL)}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/upload-miniature/{id_product}** (POST)
- **Descripción:** Set the file name 'product_'+(last product_id +1) v Upload the renamed file to aws (inside the folder: 'thumbnails/'), to serve it v Return a legend and the url

- **Parameters:**
id_product : (integer | null) (path)

- **Request Body:**   multipart/form-data
miniature : string($binary)

- **Responses:**
    - **201 Created:**
    {"message": "Miniatura subida correctamente", "url": "xxxx"} ("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/on** (POST)
- **Descripción:** Creating a product with data based on the Product model, a json, converted to str and optional thumbnail.

- **Request Body:**  multipart/form-data

product_data: string 

Ejemplo:
curl -X POST "http://localhost:8000/products/on" \
-H "Content-Type: multipart/form-data" \
-F "product_data={\"title\": \"Test\", \"price\": 99.99}" \
-F "miniature=@test.jpg"

miniature : string($binary)

- **Responses:**
    - **201 Created:**
    {"message": "Miniatura Subida y producto creado exitosamente", "product": Products(MODEL), "url":"xxxx"}("string")

    - **201 Created:**
    {"message": "Producto creado exitosamente", "product": Products(MODEL)}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/delete/{id_product}** (DELET)
- **Descripción:** Delete a product, if it has linked images in AWS S3, it is also deleted.

- **Parameters:**
id_product : integer (path)

- **Responses:**
    - **204 No Content:**
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/image/{id_image}/delete** (DELET)
- **Descripción:**  Delete the image from the Database; if it is hosted on AWS, it will also be deleted.

- **Parameters:**
id_image : integer (path)

- **Responses:**
    - **204 No Content:**
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/delete-image/** (DELET)
- **Descripción:**  Detects URL ownership based on the domain, if it is the owner, it proceeds to its elimination.

- **Request Body:**
  ```json
    {
    "id_product": 0,
    "url": "string"
    }

- **Responses:**
    - **204 No Content:**
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/update** (PUT)

- **Descripción:** Pre: The body includes the product_id. Updates the columns referring to a product in the product table.
- **Request Body:** 
  ```json
    {
    "id_product": 0,
    "title": "string",
    "description": "string",
    "price": 999999.99,
    "discount_percentage": 0,
    "rating": 0,
    "brand": "string",
    "category": "string",
    "miniature": "string"
    }

- **Responses:**
    - **200 OK:**
    {"message": "Producto Actualizado correctamente", "product": Products(MODEL)}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/up** (PUT)

- **Descripción:** Pre: the body includes the product_id; if you want to modify the thumbnail in addition to the table columns, thumbnail must be None (or equivalent) Updates both the product table columns for a product and its associated thumbnail (if any). since the form only accepts both file and text data: 'product_data' is a json construct converted to str. if you provide a url other than the one in the database and a file for the thumbnail, the file is always recognized, discarding the provided url.

- **Request Body:**  multipart/form-data

product_data: string 

Ejemplo:
"product_data={\"title\": \"Test\", \"price\": 99.99}" \ ...

miniature : string($binary)

- **Responses:**
    - **200 OK:**
    {"message": "Producto Actualizado correctamente", "product": Products(MODEL)}("string")

    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

#### **/products/all** (GET)
- **Descripción:** Returns all products and their linked images.
- **Responses:**
    - **200 OK:**
{"message": "Exito en el proseso", "products":[
    {
    "id_product": int,
    "title":str,
    "description":str,
    "price":float,
    "discountPercentage":float,
    "rating":int,
    "brand":str,
    "category":str,
    "miniature":str,
    "images":[str,str]
    },{}]
}

#### **/products/category/{category}** (GET)
- **Descripción:**
- **Parameters:**
category : string (path)

- **Responses:**
    - **200 OK:**
{"message": "Exito en el proseso", "products":[
    {
    "id_product": int,
    "title":str,
    "description":str,
    "price":float,
    "discountPercentage":float,
    "rating":int,
    "brand":str,
    "category":str,
    "miniature":str,
    "images":[str,str]
    },{}]
}
    - **404 Not Found:**
    "string"
    - **422 Unprocessable Entity:**
    {
    "detail": [
        {
        "loc": [
            "string",
            0
        ],
        "msg": "string",
        "type": "string"
        }
    ]
    }

### Environment Variables
Create a `.env` file with:
    ```env
    db_sql_database={NOMBRE_DE_LA_DATABASE}
    db_sql_host={HOST}
    db_sql_port={PUERTO}
    db_sql_password={CONTRASEÑA}
    db_sql_user={USUARIO}

    on_dev="Y" (O "N" EN CASO DE ESTAR EN PRODUCCION)

    SECRET={PALABRA_SECRETA}

    products="products"
    images="images"
    users="users"

    AWS_ACCESS_KEY_ID ="HGTGTYSTYHJJDMNCVB" (EJEMPLO)
    AWS_SECRET_ACCESS_KEY="FEGUHIFEGUFAGMdfiufgJFDBFG564/AGFD" (EJEMPLO)
    REGION="us-east-2"(LA REGION ASIGNADA POR AWS)
    CLOUDFRONT_DOMAIN ="https://abc123.cloudfront.net" (EJEMPLO)

### Execution

#### Local Environment

1. It is recommended to run the project in a virtual environment to avoid conflicts with other system dependencies.

If you do not have a virtual environment set up, you can create and activate it with the following commands:
Create a virtual environment (if you don't have one)
    python -m venv venv

Activate the virtual environment
On Windows:
    venv\Scripts\activate

On Linux/Mac:
    source venv/bin/activate

Example in terminal:
{located at project root}> python -m venv venv
{located at project root}> venv\Scripts\activate
(venv) {located at project root}>

2. Install dependencies:

Install the necessary dependencies for the project:
    pip install -r requirements.txt

3. Start the server:

Once the dependencies are installed, you can start the server with the following command:

{located at project root}> uvicorn main:app --host 0.0.0.0 --port 8000 --reload

* --reload: This flag is useful during development, as it automatically restarts the server when it detects changes in the code.

* --host 0.0.0.0: Makes the server available on all network interfaces.

* --port 8000: Defines the port on which the server will run.


The main.py file contains two important functions that verify the environment before starting the server:

4. Environment verification
check_environment_variables()
    Verifies that all environment variables are correctly defined.
        - Positive response: *---Todas las variables de entorno están definidas correctamente.---* 
        in english: *---All environment variables are correctly defined.---*
        - Negative response:  Faltan las siguientes variables de entorno: XXX, ZZZ, YYY
        in english: The following environment variables are missing: XXX, ZZZ, YYY


5. Verifica la conexión a la base de datos
is_connected()
    Verifies the connection to the database (in this case, MySQL).
        - Positive response: Conexión exitosa a la base de datos
        in english: Connection to the database successful.
        - respuesta negativa: Error al conectar a la base de datos:{error espesifico} 
        in english: Error connecting to the database: {specific error}


6. Example of terminal output:

When the server starts successfully, you will see a message similar to the following in the terminal:

INFO:     Will watch for changes in these directories: ['{ubicado en raiz del proyecto}']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [14632] using WatchFiles
*---Todas las variables de entorno están definidas correctamente.---* 
Conexión exitosa a la base de datos.
INFO:     Started server process [14040]
INFO:     Waiting for application startup.
INFO:     Application startup complete.

7. Accessing the server:

Once the server is running, you can access the API in your browser or using tools like curl, Postman, or Thunder Client:

Base URL: http://localhost:8000

If the environment variable on_dev is set to "Y", you will also have access to the interactive documentation:

Interactive documentation (Swagger UI): http://localhost:8000/docs

Alternative documentation (ReDoc): http://localhost:8000/redoc

Otherwise, if on_dev is not equal to "Y", the documentation will not be visible; 
this is especially useful for project deployment.

8. Shutdown

To stop the server: Press CTRL + C in the terminal where the server is running.

To deactivate the virtual environment: In the terminal where the virtual environment is active, run: deactivate
Example in terminal:
(venv) {ubicado en raiz del proyecto}> deactivate

#### Archivo Procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT

### Licencias
- **This project**: MIT License (ver [LICENSE](LICENSE)).
- **Dependencies**: Ver [LICENSES.md](LICENSES.md).
- **Note**: `mysql-connector-python` está bajo GPL. Si usas este código en producción, considera migrar a `pymysql` (MIT License).



