import base64
from io import BytesIO
import socket
import pickle
import pymongo
from celery import Celery
import argparse
from PIL import ImageOps
import numpy as np

app = Celery('tasks', broker='redis://localhost', backend='redis://localhost:6379')


@app.task
def guardar_imagenes_sino_existe(nombre_carpeta, objetos_imagenes):
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

@app.task
def recibir_imagenes(lista_nombres_imagenes, cliente):
    imagenes = []
    for nombre_imagen in lista_nombres_imagenes:
        imagen_bin = b""
        while True:
            imagen_parte = cliente.recv(1024)
            imagen_bin += imagen_parte
            if len(imagen_parte) < 1024:
                break
        objeto_imagen = ajuste_formato(nombre_imagen, imagen_bin)
        print(f"binario de imagen: {nombre_imagen} recibida")
        # Enviar respuesta al cliente
        cliente.sendall(b"imagen recibida")
        imagenes.append(objeto_imagen)
    cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")
    return imagenes

@app.task
def ajuste_formato(nombre_imagen, imagen_bin):
    imagen = pickle.loads(imagen_bin)
    imagen_ajustada = imagen.resize((80, 90))
    imagen_grayscale = ImageOps.grayscale(imagen_ajustada)
    buffered = BytesIO()
    imagen_grayscale.save(buffered, format="JPEG")
    # Convertir la imagen a una matriz numpy
    np_image = np.array(imagen_grayscale)
    # Aplanar la matriz numpy y convertirla en una lista de Python
    img = np_image.flatten().tolist()
    vector = [img[i]/1000 for i in range(0, len(img))]
    buffered = BytesIO()
    imagen_grayscale.save(buffered, format="JPEG")
    imagen_formateada = buffered.getvalue()
    img_base64 = base64.b64encode(imagen_formateada)
    img_str = img_base64.decode("utf-8")
    objeto_imagen = {"nombre": nombre_imagen, "imagen_str": img_str, "vector": vector}
    return objeto_imagen

@app.task
def recibir_nombre_carpeta_y_lista_nombres_imagenes(cliente):
    datos_bin = b""
    while True:
        datos_parte = cliente.recv(1024)
        datos_bin += datos_parte
        if len(datos_parte) < 1024:
            break
    datos = pickle.loads(datos_bin)
    cliente.sendall(b"nombre de carpeta y lista nombres imagenes recibidas")
    return datos[0], datos[1]

@app.task
def recibir_datos(cliente):
    nombre_carpeta, lista_nombres_imagenes = recibir_nombre_carpeta_y_lista_nombres_imagenes(cliente)
    imagenes_con_nombre = recibir_imagenes(lista_nombres_imagenes, cliente)
    # Enviar respuesta al cliente
    cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")
    # Ejecutar tarea de guardado de imágenes
    respuestas = guardar_imagenes_sino_existe(nombre_carpeta, imagenes_con_nombre)
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

    # Iniciar servidor
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((args.ip, args.puerto))
    servidor.listen(5)

    cliente, direccion = servidor.accept()
    print("Conexión desde", direccion)
    recibir_datos(cliente)
