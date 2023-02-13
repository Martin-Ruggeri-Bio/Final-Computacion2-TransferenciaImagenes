import logging
import base64
from io import BytesIO
import socket
import pickle
import pymongo
import argparse
from PIL import ImageOps
import asyncio
import numpy as np
import uuid



# Configurar el manejador de registro para escribir en un archivo
file_handler = logging.FileHandler('example.log')
file_handler.setLevel(logging.INFO)
# file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(fd)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))

# Configurar el manejador de registro para mostrar en la consola
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
# console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(fd)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S'))

# Agregar ambos manejadores al registro
logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])


async def guardar_imagenes_sino_existe(nombre_carpeta, objetos_imagenes, fd):
    try:
        cliente_mongo = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
        db = cliente_mongo.BancoImagenes
        if nombre_carpeta not in db.list_collection_names():
            db.create_collection(nombre_carpeta)
            logging.info(f"coleccion {nombre_carpeta} creada", extra={'fd': fd})
        else:
            logging.info(f"coleccion {nombre_carpeta} ya existe", extra={'fd': fd})
        coleccion = db[nombre_carpeta]
        respuestas = []
        for objeto_imagen in objetos_imagenes:
            if coleccion.find_one({'nombre': objeto_imagen['nombre']}) is None:
                coleccion.insert_one(objeto_imagen)
                respuestas.append(f"imagen {objeto_imagen['nombre']} insertada")
            else:
                respuestas.append(f"imagen {objeto_imagen['nombre']} ya existe")
        return respuestas
    except pymongo.errors.WriteError as e:
        logging.error(f"Error al insertar la imagen '{objeto_imagen['nombre']}': {e}", extra={'fd': fd})
    except pymongo.errors.ConnectionFailure as e:
        logging.error(f"Error de conexión con MongoDB: {str(e)}", extra={'fd': fd})
    except pymongo.errors.OperationFailure as e:
        logging.error(f"Error al crear la colección '{nombre_carpeta}': {e}", extra={'fd': fd})
    except Exception as e:
        logging.error(f"Error: {str(e)}", extra={'fd': fd})

async def recibir_imagenes(lista_nombres_imagenes, cliente, fd):
    try:
        imagenes = []
        for nombre_imagen in lista_nombres_imagenes:
            imagen_bin = b""
            while True:
                imagen_parte = cliente.recv(1024)
                imagen_bin += imagen_parte
                if len(imagen_parte) < 1024:
                    break
            objeto_imagen = asyncio.create_task(ajuste_formato(nombre_imagen, imagen_bin))
            logging.info(f"binario de imagen: {nombre_imagen} recibida", extra={'fd': fd})
            # Enviar respuesta al cliente
            cliente.sendall(b"imagen recibida")
            await asyncio.gather(objeto_imagen)
            objeto_imagen = objeto_imagen.result()
            imagenes.append(objeto_imagen)
    except Exception as e:
        logging.error(f"Error al recibir nombre_carpeta y lista nombres imagenes: {e}", extra={'fd': fd})
        cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")
    return imagenes


async def ajuste_formato(nombre_imagen, imagen_bin):
    try:
        imagen = pickle.loads(imagen_bin)
        imagen.show()
    except:
        logging.error(f"Error: No se pudo abrir la imagen {nombre_imagen}", extra={'fd': fd})
    try:
        imagen_ajustada = imagen.resize((80, 90))
    except:
        logging.error(f"Error: No se pudo ajustar la imagen {nombre_imagen}", extra={'fd': fd})
    try:
        imagen_grayscale = ImageOps.grayscale(imagen_ajustada)
        imagen_grayscale.show()
        # Convertir la imagen a una matriz numpy
        np_image = np.array(imagen_grayscale)
        # Aplanar la matriz numpy y convertirla en una lista de Python
        img = np_image.flatten().tolist()
        vector = [img[i]/1000 for i in range(0, len(img))]
        buffered = BytesIO()
        imagen_grayscale.save(buffered, format="JPEG")
        imagen_formateada = buffered.getvalue()
    except:
        logging.error(f"Error: No se pudo procesar la imagen {nombre_imagen}", extra={'fd': fd})
    try:
        img_base64 = base64.b64encode(imagen_formateada)
        img_str = img_base64.decode("utf-8")
    except:
        logging.error(f"Error: No se pudo codificar la imagen {nombre_imagen}", extra={'fd': fd})
    objeto_imagen = {"nombre": nombre_imagen, "imagen_str": img_str, "vector": vector}
    return objeto_imagen

async def recibir_imagenes(lista_nombres_imagenes, cliente, fd):
    try:
        imagenes = []
        for nombre_imagen in lista_nombres_imagenes:
            imagen_bin = b""
            while True:
                imagen_parte = cliente.recv(1024)
                imagen_bin += imagen_parte
                if len(imagen_parte) < 1024:
                    break
            objeto_imagen = asyncio.create_task(ajuste_formato(nombre_imagen, imagen_bin))
            logging.info(f"binario de imagen: {nombre_imagen} recibida", extra={'fd': fd})
            # Enviar respuesta al cliente
            cliente.sendall(b"imagen recibida")
            await asyncio.gather(objeto_imagen)
            objeto_imagen = objeto_imagen.result()
            imagenes.append(objeto_imagen)
    except Exception as e:
        logging.error(f"Error al recibir nombre_carpeta y lista nombres imagenes: {e}", extra={'fd': fd})
        cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")
    return imagenes

async def recibir_nombre_carpeta_y_lista_nombres_imagenes(cliente, fd):
    try:
        datos_bin = b""
        while True:
            datos_parte = cliente.recv(1024)
            datos_bin += datos_parte
            if len(datos_parte) < 1024:
                break
        datos = pickle.loads(datos_bin)
    except Exception as e:
        logging.error(f"Error al recibir los datos: {e}", extra={'fd': fd})
    cliente.sendall(b"nombre de carpeta y lista nombres imagenes recibidas")
    return datos


async def recibir_datos(cliente, fd):
    try:
        datos = asyncio.create_task(recibir_nombre_carpeta_y_lista_nombres_imagenes(cliente, fd))
        await asyncio.gather(datos)
        datos = datos.result()
        nombre_carpeta, lista_nombres_imagenes = datos[0], datos[1]

        imagenes_con_nombre = asyncio.create_task(recibir_imagenes(lista_nombres_imagenes, cliente, fd))
        await asyncio.gather(imagenes_con_nombre)
        imagenes_con_nombre = imagenes_con_nombre.result()
    except Exception as e:
        logging.error(f"Error al recibir los datos: {e}", extra={'fd': fd})
        cliente.close()
        return

    try:
        # Enviar respuesta al cliente
        cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")

        # Ejecutar tarea de guardado de imágenes
        respuestas = asyncio.create_task(guardar_imagenes_sino_existe(nombre_carpeta, imagenes_con_nombre, fd))
        await asyncio.gather(respuestas)
        respuestas = respuestas.result()
    except Exception as e:
        logging.error(f"Error al guardar las imágenes: {e}", extra={'fd': fd})

    for objeto_imagen in imagenes_con_nombre:
        logging.info(objeto_imagen['nombre'], extra={'fd': fd})
    for respuesta in respuestas:
        logging.info(respuesta, extra={'fd': fd})
    logging.info("fin", extra={'fd': fd})

    # Cerrar conexión
    cliente.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de procesamiento de imágenes")
    parser.add_argument("-i", "--ip", help="Dirección IP", type=str, default='0.0.0.0')
    parser.add_argument("-p", "--puerto", help="Puerto", type=int, default='5001')
    args = parser.parse_args()


    try:
        # Iniciar servidor
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((args.ip, args.puerto))
        servidor.listen(5)
        logging.info("Servidor iniciado en IP %s, puerto %d" % (args.ip, args.puerto), extra={'fd': 0})
    except Exception as e:
        logging.error("Error al iniciar el servidor: %s" % e, extra={'fd': 0})
        exit()

    while True:
        try:
            cliente, direccion = servidor.accept()
            # loguear el filedescriptor dl cliente que nos conectamos por socket
            # fd = cliente.fileno()
            fd = uuid.uuid4()
            logging.info("Conexión desde %s" % str(direccion), extra={'fd': fd})
            asyncio.run(recibir_datos(cliente, fd))
        except KeyboardInterrupt:
            logging.info("Programa interrumpido por el usuario", extra={'fd': fd})
            break
        except Exception as e:
            logging.error("Error durante la comunicación con el cliente: %s" % e, extra={'fd': fd})
