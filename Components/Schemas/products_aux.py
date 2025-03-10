#importaciones internas
from fastapi import status, HTTPException
from botocore.exceptions import ClientError
import mysql.connector
import boto3

from Components.constants import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY, REGION, DATABASE,PRODUCTS,CLOUDFRONT_DOMAIN
from DB.client import get_sql_connection


def json_product(json:list[tuple]):
    """
    ES: Transformar una lista[tupla] en un diccionario basado en el Objeto: Product
    EN: Transform a list[tuple] into a dictionary based on the Object: Product
    """
    print(json[0])
    return{
        "id_product" : json[0][0],
        "title": json[0][1],
        "description": json[0][2],
        "price": float(json[0][3]),
        "discount_percentage": float(json[0][4]),
        "rating": int(json[0][5]) if json[0][5] is not None else None,
        "brand":json[0][6],
        "category": json[0][7],
        "miniature": str(json[0][8]) if json[0][8] is not None else None,
    }


def search_images(id_product:int):
    """
    ES: busca existencia de imagenes vinculadas a un id_procts.
    retorna: [(),()]
    EN: Search for the existence of images linked to a id_procts.
    returns: [(),()]
    """
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                # Solicito id_cliente para particularizar direccion. 
                query=f"""
                SELECT *
                FROM {DATABASE}.images
                WHERE id_product = %s;
                """
                cursor.execute(query,(id_product,))
                result = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error en la consulta a la base de datos: {e}")
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= str(e)
        )
    except Exception as e:
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return result

def captura(db,tabla,columna,comparacion):
    """
    ES:
    db -> Base de datos la que se consulta
    tabla -> Tabla consultada
    columna -> Columna indivisualizada
    comparacion -> clave de consulta
    retorna igualdades en fromato [(),()]
    EN:
    db -> Database being queried
    table -> Queried table
    column -> Individual column
    comparison -> query key
    returns equalities in the format [(),()]
    """
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                # Solicito id_cliente para particularizar direccion. 
                query=f"""
                SELECT *
                FROM {db}.{tabla}
                WHERE {columna} = %s;
                """
                cursor.execute(query,(comparacion,))
                result = cursor.fetchall()
    except mysql.connector.Error as e:
        print(f"Error en la consulta a la base de datos: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return result

def last_id(DB, TABLE, COLUMN):
    """
    ES:
    DB -> Base de datos la que se consulta
    TABLE -> Tabla consultada
    COLUMN -> Columna indivisualizada
    retorna, el id mas alto.
    EN: 
    DB -> Database being queried
    TABLA -> Queried table
    COLUMN -> Individual column
    returns the highest id.
    """
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""
                SELECT MAX({COLUMN}) AS last_id
                FROM {DB}.{TABLE};
                """
                cursor.execute(query)
                result = cursor.fetchone()
                return result[0] if result[0] else 0
            
    except mysql.connector.Error as e:
        print(f"Error en la consulta a la base de datos: {e}")
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def miniature_on_product(id_prodict:int, url:str):
    """
    ES:
    Función para la inyeccion de la url de la miniatura de un producto.
    EN: 
    Function for injecting the URL of a product thumbnail.
    """
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""
                UPDATE {DATABASE}.{PRODUCTS}
                SET miniature = %s 
                WHERE id_product = %s
                ;
                """
                cursor.execute(query,(url,id_prodict))
                connection.commit()
                # Verificar si se actualizó alguna fila
                if cursor.rowcount == 0:
                    raise ValueError("No se encontró ningún producto con el ID proporcionado.")
    except mysql.connector.Error as e:
        print(f"Error en la consulta a la base de datos: {e}")
        HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail= str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

def delete_miniature(url:str):
    """
    ES: Elimina de ser posible de AWS S3 la miniatura probista por url.
    EN: Remove the probista thumbnail by url from AWS S3 if possible.
    """
    if f"{CLOUDFRONT_DOMAIN}/miniatures/" in url:
        try:
            # Extraer el nombre del archivo de la URL
            file_name = url.split("/")[-1]
            bucket_name = "ecomers.test.load"  # Nombre de tu bucket de S3

            # Crear un cliente de S3
            s3 = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=REGION,
            )

            # Eliminar el archivo de S3
            s3.delete_object(Bucket=bucket_name, Key=f"miniatures/{file_name}")

        except ClientError as e:
            # Manejar errores específicos de AWS
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la imagen de AWS S3."
            )
    else:
        print("La imagen no pertenece a tu bucket de AWS S3. Solo se desvinculara.")
