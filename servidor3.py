import base64
from io import BytesIO
import socket
import pickle
import pymongo
from celery import Celery
import argparse
from PIL import Image, ImageOps

app = Celery("task", broker="redis://localhost:6379/0")


@app.task
def guardar_imagenes_sino_existe(nombre_carpeta, objetos_imagenes):
    try:
        cliente_mongo = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
    except pymongo.errors.ConnectionFailure as e:
        print("Error al conectarse a MongoDB:", e)
    db = cliente_mongo.BancoImagenes
    if nombre_carpeta not in db.list_collection_names():
        db.create_collection(nombre_carpeta)
    coleccion = db[nombre_carpeta]
    respuesta = []
    for objeto_imagen in objetos_imagenes:
        if coleccion.find_one(objeto_imagen) is None:
            coleccion.insert_one(objeto_imagen)
            respuesta.append(f"imagen {objeto_imagen.keys()} insertada")
        else:
            respuesta.append(f"imagen {objeto_imagen.keys()} ya existe")
    return respuesta


@app.task
def ajuste_formato(nombre_imagen, img_str):
    img_bytes = img_str.encode("utf-8")
    img_decoded = base64.b64decode(img_bytes)
    imagen = Image.open(BytesIO(img_decoded))
    imagen_ajustada = imagen.resize((80, 90))
    imagen_grayscale = ImageOps.grayscale(imagen_ajustada)
    buffered = BytesIO()
    imagen_grayscale.save(buffered, format="JPEG")
    imagen_formateada = buffered.getvalue()
    img_base64 = base64.b64encode(imagen_formateada)
    img_str = img_base64.decode("utf-8")
    objeto_imagen = {nombre_imagen: img_str}
    return objeto_imagen



def recibir_datos(cliente):
    datos_bin = b""
    while True:
        datos_parte = cliente.recv(1024)
        datos_bin += datos_parte
        if len(datos_parte) < 1024:
            break
    datos = pickle.loads(datos_bin)
    cliente.sendall(b"nombre de carpeta y lista nombres imagenes recibidas")
    nombre_carpeta, lista_nombres_imagenes = datos[0], datos[1]

    imagenes_con_nombre = []
    for nombre_imagen in lista_nombres_imagenes:
        imagen_bin = b""
        while True:
            imagen_parte = cliente.recv(1024)
            imagen_bin += imagen_parte
            if len(imagen_parte) < 1024:
                break
        imagen = pickle.loads(imagen_bin)

        # Convertir imagen en una secuencia de bytes
        buffer = BytesIO()
        imagen.save(buffer, format='JPEG')
        imagen_bytes = buffer.getvalue()
        img_base64 = base64.b64encode(imagen_bytes)
        img_str = img_base64.decode("utf-8")

        objeto_imagen = ajuste_formato.delay(nombre_imagen, img_str)
        print(f"binario de imagen: {nombre_imagen} recibida")
        # Enviar respuesta al cliente
        cliente.sendall(b"imagen recibida")
        imagenes_con_nombre.append(objeto_imagen.get())
    # Enviar respuesta al cliente
    cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")

    # Ejecutar tarea de guardado de imágenes
    respuestas = guardar_imagenes_sino_existe.delay(nombre_carpeta, imagenes_con_nombre)


    for imagen in imagenes_con_nombre:
        print(imagen.keys())

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
