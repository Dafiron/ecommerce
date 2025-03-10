#Importacion Externa // External Import
from fastapi import APIRouter, status, HTTPException,UploadFile, File, Form
from fastapi.responses import Response
from botocore.exceptions import ClientError
from typing import List
from json import loads, JSONDecodeError
import boto3
import mysql.connector
import os


#Importacion Interna // Internal Import
from Components.constants import AWS_ACCESS_KEY_ID,AWS_SECRET_ACCESS_KEY, REGION, DATABASE, IMAGES, PRODUCTS, MAX_FILES_ALLOWED,CLOUDFRONT_DOMAIN, ALLOWED_IMAGE_TYPES
from Components.Schemas.products_aux import search_images, captura, last_id, json_product, miniature_on_product, delete_miniature
from DB.client import get_sql_connection
from Components.models import Products, Image

router= APIRouter(
    prefix="/products",
    tags=["products"],
    responses={status.HTTP_404_NOT_FOUND:{"message":"No encontrado"}}
    )



@router.get("")
async def testigo ():
    return "products listo para el ingreso de datos"


@router.post("/upload-image/{id_product}",status_code=status.HTTP_201_CREATED)
async def upload_image(id_product:int, image: UploadFile = File(...)):
    """
    ES: Establece, el nombre del archivo a travez de la consulta si existen otras imagenes vinculadas al id_products
        v
    Sube el archivo renombrado a aws, para servirlo
        v
    Retornado una leyenda y la url
    EN: Set the file name by querying if there are other images linked to the id_products
        v
    Upload the renamed file to aws, to serve it
        v
    Returns a legend and the url
    """
    try:
        # Validar que el archivo sea una imagen
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Tipo de archivo no permitido"
            )
        
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=REGION,
        )
        bucket_name = "ecomers.test.load"
        last_image_id = last_id(DATABASE,IMAGES,"id_image")
        images_db=search_images(id_product)
        if len(images_db) >= MAX_FILES_ALLOWED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Error al subir la imagen: EL Producto tiene el maximo de imagenes asociadas"
            )
        
        new_image_name = f"images/{id_product}-{last_image_id + 1}.{image.filename.split('.')[-1]}"

        # Guardar temporalmente la imagen
        temp_path = f"temp_{id_product}-{last_image_id + 1}.{image.filename.split('.')[-1]}"
        with open(temp_path, "wb") as f:
            f.write(await image.read())

        # Subir la imagen a S3
        s3.upload_file(
            temp_path, bucket_name, 
            new_image_name,
            ExtraArgs={"ContentType": image.content_type}
        )

        url = f"{CLOUDFRONT_DOMAIN}/{new_image_name}"

        # Eliminar el archivo temporal
        os.remove(temp_path)

        return {"message": "Imagen subida exitosamente", "url": url}

    except HTTPException as http_exc:
        # Capturar errores HTTP específicos (como el 400)
        raise http_exc

    except Exception as e:
        # Capturar otros errores generales
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Error al subir la imagen: {str(e)}"
        )


@router.post("/image/{id_product}/on", status_code=status.HTTP_201_CREATED)
async def image_on(id_product: int, images: List[UploadFile] = File(...)):
    """
    ES: Pre: El producto es valido y existe en Base de datos.
    Agrega una imagen al producto previamente creado. subiendo y sirviendolo en AWS S3; 
    Luego se hacen las inyecciones en base de datos pertinentes.
    EN: Pre: The product is valid and exists in the database
    Add an image to the previously created product, uploading and serving it to AWS S3;
    Then the relevant database injections are made.
    """
    try:
        # Validar que el producto existe
        if not captura(DATABASE, PRODUCTS, "id_product", id_product):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El producto no existe"
            )
        cant_image_as= len(captura(DATABASE, IMAGES, "id_product", id_product))
        images_on = len(images)
        if (cant_image_as + images_on)> MAX_FILES_ALLOWED:
            raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"El Producto ya cuenta con {cant_image_as}, resultando imposible agregarle {images_on} imagenes; Debido a que {MAX_FILES_ALLOWED} es el maximo. "
                )
        # Procesar cada imagen
        uploaded_images = []
        for image in images:
            # Subir la imagen a S3
            res_dict = await upload_image(id_product, image)
            # Registrar la URL en la base de datos
            with get_sql_connection() as connection:
                with connection.cursor() as cursor:
                    query = f"""
                    INSERT INTO {DATABASE}.images
                    (id_product, image_url)
                    VALUES (%s, %s);
                    """
                    cursor.execute(query, (id_product, res_dict["url"]))
                    connection.commit()
            # Guardar la URL para la respuesta
            uploaded_images.append(res_dict["url"])

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir las imágenes: {str(e)}"
        )

    return {"message": "Imágenes subidas exitosamente", "urls": uploaded_images}




@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_product(product: Products):
    """
    ES: Creacion de producto, con el modelo Products.
    Si se provee id_porducts, NO se toma en consideracion.
    Respuesta afirmativa a la creación 201 -> {"message": str, "product": Products }
    EN: Product creation, with the Products model, and the thumbnail if it exists.
    If id_product is provided, it is NOT taken into consideration.
    Affirmative response to creation 201 -> {"message": str, "product": Products }
    """

    try:
        # Crear el producto en la base de datos
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""
                INSERT INTO {DATABASE}.products (
                    title, description, price, discount_percentage, rating, brand, category
                ) VALUES (%s, %s, %s, %s, %s, %s, %s);
                """
                cursor.execute(
                    query,
                    (
                        product.title,
                        product.description,
                        product.price,
                        product.discount_percentage,
                        product.rating,
                        product.brand,
                        product.category
                    )
                )
                id_product = cursor.lastrowid
                connection.commit()
                new_product= json_product(captura(DATABASE, PRODUCTS,"id_product",id_product))

            return {"message": "Producto creado exitosamente", "product": Products(**new_product)}

    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el producto: {str(e)}"
        )


@router.post("/upload-miniature/{id_product}", status_code=status.HTTP_201_CREATED)
async def upload_miniature(miniature: UploadFile, id_product: int |None = None):
    """
    ES: Establece, el nombre del archivo  'product_'+(ultimo id_product +1)
        v
    Sube el archivo renombrado a aws (dentro de la carpeta:'miniatures/') , para servirlo
        v
    Retornado una leyenda y la url
    EN: Set the file name 'product_'+(last product_id +1)
    v
    Upload the renamed file to aws (inside the folder:'thumbnails/') , to serve it
    v
    Returns a legend and the url
    """

    if miniature and miniature.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tipo de archivo no permitido"
        )
    try:
        s3 = boto3.client(
            's3',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=REGION,
        )
        bucket_name = "ecomers.test.load"

        if not id_product:
            id_product = last_id(DATABASE,PRODUCTS,"id_product")
        # Generar el nombre del archivo con la carpeta `miniatures/`
        file_extension = miniature.filename.split('.')[-1]
        miniature_name = f"miniatures/product_{id_product}.{file_extension}"

        # Guardar temporalmente la miniatura
        temp_path = f"temp_product_{id_product}.{file_extension}"
        with open(temp_path, "wb") as f:
            f.write(miniature.file.read())

        # Subir la miniatura a S3
        s3.upload_file(
            temp_path,
            bucket_name,
            miniature_name,
            ExtraArgs={"ContentType": miniature.content_type}
        )

        # Generar la URL con CloudFront
        url = f"{CLOUDFRONT_DOMAIN}/{miniature_name}"

        # Eliminar el archivo temporal
        os.remove(temp_path)

        return {"message": "Miniatura subida correctamente", "url": url}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir la miniatura: {str(e)}"
        )


@router.post("/on", status_code=status.HTTP_201_CREATED)
async def product_on(product_data: str = Form(...), miniature: UploadFile = File(None)):
    """
    ES: Creación de producto con datos con base al modelo Product, un json, converso a str y miniatura opcional.
    EN: Creating a product with data based on the Product model, a json, converted to str and optional thumbnail.
    """
    try:
        # Convertir el campo `product_data` de texto a JSON
        product_dict = loads(product_data)

        # Validar los datos del producto usando el modelo Pydantic
        product = Products(**product_dict)

        re_product = await create_product(product)

        if miniature:
            re_miniature = await upload_miniature(miniature, re_product["product"].id_product)
            miniature_on_product(re_product["product"].id_product,re_miniature["url"])
            return {"message": "Miniatura Subida y producto creado exitosamente", "product": re_product["product"], "url":re_miniature["url"]}
        else:
            return re_product

    except JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'product_data' no es un JSON válido"
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el producto: {str(e)}"
        )

@router.delete("/delete/{id_product}", status_code=status.HTTP_204_NO_CONTENT)
async def product_delete(id_product: int):
    """
    ES: Elimina un producto, si este tiene imagenes vinculadas en AWS S3, tambien se prosede a su eliminacion.
    EN: Delete a product, if it has linked images in AWS S3, it is also deleted.
    """
    product = captura(DATABASE,PRODUCTS,"id_product",id_product)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se encontro el id del producto provisto."
        )
    images = captura(DATABASE,IMAGES,"id_product",id_product)
    try:
        with get_sql_connection() as connection:
                with connection.cursor() as cursor:
                    query = (
                        f"""
                        DELETE FROM {DATABASE}.{PRODUCTS}
                        WHERE id_product = %s;
                        """
                    )
                    cursor.execute(
                        query,(
                        id_product,
                    ))
                    connection.commit()
                    miniature_url = product[0][-1]
                    if miniature_url:
                        # Extraer el nombre del archivo y verificar si pertenece a tu bucket
                        delete_miniature(miniature_url)
                if images:
                    for image in images:
                        await delete_image(Image(url=image[-1]))

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
            )
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )




@router.delete("/image/{id_image}/delete", status_code=status.HTTP_204_NO_CONTENT)
async def image_delete(id_image:int):
    """
    ES: Elimina la imagen de Base de datos; sí esta esta alojada en AWS, tambien se prosede a su eliminacion.
    EN: Delete the image from the Database; if it is hosted on AWS, it will also be deleted.
    """
    image = captura(DATABASE,PRODUCTS,"id_image",id_image)
    if not image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se encontro el id de la imagen provista."
        )
    try:
        with get_sql_connection() as connection:
                with connection.cursor() as cursor:
                    query = (
                        f"""
                        DELETE FROM {DATABASE}.{IMAGES}
                        WHERE id_image = %s;
                        """
                    )
                    cursor.execute(
                        query,(
                        id_image,
                    ))
                    connection.commit()
                    image_url = image[0][-1]
                    if image_url:
                        await delete_image(Image(url=image_url))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
            )
    return Response(
        status_code=status.HTTP_204_NO_CONTENT,
    )

@router.delete("/delete-image/",status_code=status.HTTP_204_NO_CONTENT)
async def delete_image(image:Image):
    """
    ES: Detecta Pertenencia del url en base al dominio, de ser propietario, prosede a su eliminacion.
    EN: Detects URL ownership based on the domain, if it is the owner, proceeds to its elimination.
    """
    image_url = image.url
    # Extraer el nombre del archivo y verificar si pertenece a tu bucket
    if f"{CLOUDFRONT_DOMAIN}/images/" in image_url:
        try:
            # Extraer el nombre del archivo de la URL
            file_name = image_url.split("/")[-1]
            bucket_name = "ecomers.test.load"  # Nombre de tu bucket de S3

            # Crear un cliente de S3
            s3 = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=REGION,
            )

            # Eliminar el archivo de S3
            s3.delete_object(Bucket=bucket_name, Key=f"images/{file_name}")

        except ClientError as e:
            # Manejar errores específicos de AWS
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al eliminar la imagen de AWS S3."
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
                )
    else:
        print("La imagen no pertenece a tu bucket de AWS S3. Solo se desvinculara.")

@router.put("/update",status_code=status.HTTP_200_OK)
async def product_update(product: Products):
    """
    ES: Pre: el cuerpo incluye el id_product.
    Actualiza las columnas resferentes a un producto en la tabla product.
    EN: Pre: The body includes the id_product. 
    Updates the columns referring to a product in the product table.
    """
    if not product.id_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se detecto el pre-requisito de incluir id_product."
        )
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query = f"""
                UPDATE {DATABASE}.{PRODUCTS}
                SET miniature = %s ,
                    title = %s, 
                    description =%s, 
                    price =%s, 
                    discount_percentage =%s, 
                    rating =%s, brand =%s, 
                    category =%s, 
                    miniature =%s
                WHERE id_product = %s
                ;
                """
                cursor.execute(query,(
                    product.miniature,
                    product.title,
                    product.description,
                    product.price,
                    product.discount_percentage,
                    product.rating,
                    product.brand,
                    product.category,
                    product.miniature,
                    product.id_product
                    ))
                connection.commit()
                # Verificar si se actualizó alguna fila
                if cursor.rowcount == 0:
                    raise ValueError("No se encontró ningún producto con el ID proporcionado.")
                new_product= json_product(captura(DATABASE, PRODUCTS,"id_product",product.id_product))

                return {"message": "Producto Actualizado correctamente", "product": Products(**new_product)}
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

@router.put("/up",status_code=status.HTTP_200_OK)
async def product_up(product_data: str = Form(...), miniature: UploadFile = File(None)):
    """
    ES: Pre: el cuerpo incluye el id_product; si se busca modificar la miniatura ademas de las columnas de la tabla, miniatura debe ser None(o quivalente)
    Actualiza tanto las comuna de la tabla product en lo referente a un producto como a su miniatura asociada (si la ubiese).
    dado que form solo hacepta tanto datos file como text: 'product_data' es un constructo json comberso a str.
    si se provee un url distiento del que se tiene en base de datos y un archivo file para la miniatura prima simpre el file descartando el url provisto.
    EN: Pre: the body includes the id_product; if you want to modify the thumbnail in addition to the table columns, thumbnail must be None (or equivalent)
    Updates both the product table columns for a product and its associated thumbnail (if any).
    since the form only accepts both file and text data: 'product_data' is a json construct converted to str.
    if you provide a different url from the one in the database and a file for the thumbnail, the file is always used, discarding the provided url.
    """
    try:
        # Convertir el campo `product_data` de texto a JSON
        product_dict = loads(product_data)

        # Validar los datos del producto usando el modelo Pydantic
        product = Products(**product_dict)

        if not product.id_product:
            raise HTTPException(
                status_code = status.HTTP_400_BAD_REQUEST,
                detail="No se encontro en el cuerpo el id_product"
            )

        product_db = json_product(captura(DATABASE,PRODUCTS,"id_product",product.id_product))

        product_db = Products(**product_db)

        if not product.miniature or product.miniature != product_db.miniature:
            if miniature and product_db.miniature == None:
                re_miniature = await upload_miniature(miniature, product.id_product)
                product.miniature = re_miniature["url"]
            elif miniature and product_db.miniature != None:
                delete_miniature(product_db.miniature)
                re_miniature = await upload_miniature(miniature, product.id_product)
                product.miniature = re_miniature["url"]
            elif not miniature and product_db.miniature != None:
                delete_miniature(product_db.miniature)
        re_product= await product_update(product)
        
        return re_product

    except JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El campo 'product_data' no es un JSON válido"
        )
    except HTTPException as http_exc:
        raise http_exc
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear el producto: {str(e)}"
        )

@router.get("/all",status_code=status.HTTP_200_OK)
async def all():
    """
    ES: Restona todos productos y sus imagenes vinculadas.
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
    },{}]}
    EN: Restore all products and their linked images.
    """
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query=f"""
                SELECT *
                FROM {DATABASE}.{PRODUCTS}
                """
                cursor.execute(query,)
                result = cursor.fetchall()
                query2 = f"""
                SELECT *
                FROM {DATABASE}.{IMAGES}
                """
                cursor.execute(query2,)
                result2 = cursor.fetchall()
                images = {}
                for im in result2:
                    if not im[1] in images:
                        images[im[1]]=[]
                    images[im[1]].append(im[2])
                res = {"message": "Exito en el proseso", "products":[]}
                for r in result:
                    print(f"en proceso: {r}")
                    res["products"].append({
                        "id_product":r[0],
                        "title":r[1],
                        "description":r[2],
                        "price":r[3],
                        "discountPercentage":r[4],
                        "rating":r[5],
                        "brand":r[6],
                        "category":r[7],
                        "miniature":r[8],
                        "images":images[r[0]] if r[0] in images else []
                    })
                return res

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

@router.get("/category/{category}",status_code=status.HTTP_200_OK)
async def search_category(category:str):
    """
    ES: Retorna todos productos de determinada categoria y sus imagenes vinculadas .
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
    },{}]}
    EN: Returns all products in a certain category and their linked images.
    """
    try:
        with get_sql_connection() as connection:
            with connection.cursor() as cursor:
                query=f"""
                SELECT *
                FROM {DATABASE}.{PRODUCTS}
                WHERE category = %s
                """
                cursor.execute(query,(category,))
                result = cursor.fetchall()
                ids= [r[0] for r in result]
                query2 = f"""
                SELECT *
                FROM {DATABASE}.{IMAGES}
                WHERE id_product in ({','.join(map(str, ids))})
                """
                cursor.execute(query2,)
                result2 = cursor.fetchall()
                images = {}
                for im in result2:
                    if not im[1] in images:
                        images[im[1]]=[]
                    images[im[1]].append(im[2])
                res = {"message": "Exito en el proseso", "products":[]}
                for r in result:
                    print(f"en proceso: {r}")
                    res["products"].append({
                        "id_product":r[0],
                        "title":r[1],
                        "description":r[2],
                        "price":r[3],
                        "discountPercentage":r[4],
                        "rating":r[5],
                        "brand":r[6],
                        "category":r[7],
                        "miniature":r[8],
                        "images":images[r[0]] if r[0] in images else []
                    })
                return res

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