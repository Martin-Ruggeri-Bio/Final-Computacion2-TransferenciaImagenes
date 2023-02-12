from io import BytesIO
import socket
import pickle
import pymongo
import argparse
from PIL import ImageOps
import asyncio
import numpy as np

async def guardar_imagenes_sino_existe(nombre_carpeta, objetos_imagenes):
    try:
        cliente_mongo = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
        db = cliente_mongo.BancoImagenes
        if nombre_carpeta not in db.list_collection_names():
            db.create_collection(nombre_carpeta)
            print(f"coleccion {nombre_carpeta} creada")
        else:
            print(f"coleccion {nombre_carpeta} ya existe")
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
        respuestas.append(f"Error al insertar la imagen '{objeto_imagen['nombre']}': {e}")
    except pymongo.errors.ConnectionFailure as e:
        print(f"Error de conexión con MongoDB: {str(e)}")
    except pymongo.errors.OperationFailure as e:
        print(f"Error al crear la colección '{nombre_carpeta}': {e}")
    except Exception as e:
        print(f"Error: {str(e)}")

async def recibir_imagenes(lista_nombres_imagenes, cliente):
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
            print(f"binario de imagen: {nombre_imagen} recibida")
            # Enviar respuesta al cliente
            cliente.sendall(b"imagen recibida")
            await asyncio.gather(objeto_imagen)
            objeto_imagen = objeto_imagen.result()
            imagenes.append(objeto_imagen)
    except Exception as e:
        print(f"Error al recibir nombre_carpeta y lista nombres imagenes: {e}")
    cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")
    return imagenes


async def ajuste_formato(nombre_imagen, imagen_bin):
    try:
        imagen = pickle.loads(imagen_bin)
        imagen.show()
    except:
        return f"Error: No se pudo abrir la imagen {nombre_imagen}"
    try:
        imagen_ajustada = imagen.resize((80, 90))
    except:
        return f"Error: No se pudo ajustar la imagen {nombre_imagen}"
    try:
        imagen_grayscale = ImageOps.grayscale(imagen_ajustada)
        imagen_grayscale.show()
        # # Convertir la imagen a una matriz numpy
        # np_image = np.array(imagen_grayscale)
        # # Aplanar la matriz numpy y convertirla en una lista de Python
        # img = np_image.flatten().tolist()
        # vector = [img[i]/1000 for i in range(0, len(imagen))]
    except:
        return f"Error: No se pudo procesar la imagen {nombre_imagen}"
    # objeto_imagen = {"nombre": nombre_imagen, "imagen_str": imagen_grayscale, "vector": vector}
    objeto_imagen = {"nombre": nombre_imagen, "imagen_str": imagen_grayscale}
    
    return objeto_imagen

async def recibir_nombre_carpeta_y_lista_nombres_imagenes(cliente):
    try:
        datos_bin = b""
        while True:
            datos_parte = cliente.recv(1024)
            datos_bin += datos_parte
            if len(datos_parte) < 1024:
                break
        datos = pickle.loads(datos_bin)
    except Exception as e:
        print(f"Error al recibir los datos: {e}")
    cliente.sendall(b"nombre de carpeta y lista nombres imagenes recibidas")
    return datos


async def recibir_datos(cliente):
    try:
        datos = asyncio.create_task(recibir_nombre_carpeta_y_lista_nombres_imagenes(cliente))
        await asyncio.gather(datos)
        datos = datos.result()
        nombre_carpeta, lista_nombres_imagenes = datos[0], datos[1]

        imagenes_con_nombre = asyncio.create_task(recibir_imagenes(lista_nombres_imagenes, cliente))
        await asyncio.gather(imagenes_con_nombre)
        imagenes_con_nombre = imagenes_con_nombre.result()
    except Exception as e:
        print(f"Error al recibir los datos: {e}")
        cliente.close()
        return

    try:
        # Enviar respuesta al cliente
        cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")

        # Ejecutar tarea de guardado de imágenes
        respuestas = asyncio.create_task(guardar_imagenes_sino_existe(nombre_carpeta, imagenes_con_nombre))
        await asyncio.gather(respuestas)
        respuestas = respuestas.result()
    except Exception as e:
        print(f"Error al guardar las imágenes: {e}")

    for objeto_imagen in imagenes_con_nombre:
        print(objeto_imagen['nombre'])
    for respuesta in respuestas:
        print(respuesta)
    print("fin")

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
    except Exception as e:
        print(f"Error al iniciar el servidor: {e}")
        exit()

    while True:
        try:
            cliente, direccion = servidor.accept()
            print("Conexión desde", direccion)
            asyncio.run(recibir_datos(cliente))
        except KeyboardInterrupt:
            print("\nPrograma interrumpido por el usuario")
            break
        except Exception as e:
            print(f"Error durante la comunicación con el cliente: {e}")
