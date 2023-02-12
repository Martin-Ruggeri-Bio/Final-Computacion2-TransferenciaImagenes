from ast import Break
import base64
import socket
import pickle
import zlib
import pymongo
from celery import Celery
import argparse

app = Celery("tareas", broker="redis://localhost:6379/0")


# @app.task
def crear_coleccion_sino_existe(nombre_carpeta):
    cliente_mongo = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
    db = cliente_mongo.BancoImagenes
    coleccion = db[nombre_carpeta]
    coleccion.drop()
    if nombre_carpeta not in db.list_collection_names():
        db.create_collection(nombre_carpeta)
        print(f"coleccion {nombre_carpeta} creada")
    else:
        print(f"coleccion {nombre_carpeta} ya existe")

# @app.task
# def guardar_imagenes_sino_existe(nombre_carpeta, imagenes):
#     cliente_mongo = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
#     db = cliente_mongo.BancoImagenes
#     coleccion = db[nombre_carpeta]
#     for imagen in imagenes:
#         # imagen_codificada = base64.b64encode(imagen).decode('utf-8')
#         if coleccion.find_one({"imagen": imagen}) is None:
#             coleccion.insert_one({"imagen": imagen})

# # @app.task
# def guardar_nombres_de_imagenes_sino_existe(lista_nombres_imagenes):
#     cliente_mongo = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
#     db = cliente_mongo.BancoImagenes
#     coleccion = db.nombre_de_imagenes
#     for imagen in lista_nombres_imagenes:
#         if coleccion.find_one({"imagen": imagen}) is None:
#             coleccion.insert_one({"imagen": imagen})
#         else:
#             print(f"imagen {imagen} ya existe")

def guardar_imagenes_sino_existe(nombre_carpeta, objetos_imagenes):
    cliente_mongo = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
    db = cliente_mongo.BancoImagenes
    coleccion = db[nombre_carpeta]
    for objeto_imagen in objetos_imagenes:
        if coleccion.find_one(objeto_imagen) is None:
            coleccion.insert_one(objeto_imagen)
            print(f"imagen {objeto_imagen.keys()} insertada")
        else:
            print(f"imagen {objeto_imagen.keys()} ya existe")

def recibir_imagenes(lista_nombres_imagenes, cliente):
    imagenes = []
    for imagen in lista_nombres_imagenes:
        imagen_bin = b""
        while True:
            imagen_parte = cliente.recv(1024)
            imagen_bin += imagen_parte
            if len(imagen_parte) < 1024:
                break
        try:
            imagen_descomprimida = zlib.decompress(imagen_bin)
            # Unir binario de la imagen al nombre de la imagen
            objeto_imagen = {imagen: imagen_descomprimida}
            print(f"binario de imagen: {imagen} recibida")
        except zlib.error as e:
            print(f"Error al descomprimir imagen: {e}")
            cliente.close()
        # Enviar respuesta al cliente
        cliente.sendall(b"imagen recibida")
        imagenes.append(objeto_imagen)
    cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")
    return imagenes


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


def recibir_datos(cliente):

    nombre_carpeta, lista_nombres_imagenes = recibir_nombre_carpeta_y_lista_nombres_imagenes(cliente)

    # Enviar respuesta al cliente
    # cliente.sendall(b"ok")

    # Ejecutar tarea de creación de colección
    # crear_coleccion_sino_existe.delay(nombre_carpeta)
    crear_coleccion_sino_existe(nombre_carpeta)

    imagenes_con_nombre = recibir_imagenes(lista_nombres_imagenes, cliente)
    print(imagenes_con_nombre[0].keys())
    
    # Enviar respuesta al cliente
    cliente.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")

    # Ejecutar tarea de guardado de imágenes
    guardar_imagenes_sino_existe(nombre_carpeta, imagenes_con_nombre)

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
