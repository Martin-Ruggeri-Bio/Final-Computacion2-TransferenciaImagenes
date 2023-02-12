import base64
from io import BytesIO
import signal
import pickle
import socketserver
import threading
import pymongo
import argparse
from celery import Celery
from PIL import Image, ImageOps

app = Celery("task", broker="redis://localhost:6379/0")


@app.task
def guardar_imagenes_sino_existe(nombre_carpeta, objetos_imagenes):
    cliente_mongo = pymongo.MongoClient("mongodb://root:root@localhost:27017/")
    db = cliente_mongo.BancoImagenes
    if nombre_carpeta not in db.list_collection_names():
        db.create_collection(nombre_carpeta)
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
    objeto_imagen = {"nombre": nombre_imagen, "imagen_str": img_str}
    return objeto_imagen


class MyTCPHandler(socketserver.BaseRequestHandler):
    # la funcion handle nos va a permitir que cuando se ejecute el servidor
    # quiero que la conexion con ese cliente se maneje de esta manera
    def handle(self):
        datos_bin = b""
        while True:
            datos_parte = self.request.recv(1024)
            datos_bin += datos_parte
            if len(datos_parte) < 1024:
                break
        datos = pickle.loads(datos_bin)
        self.request.sendall(b"nombre de carpeta y lista nombres imagenes recibidas")
        nombre_carpeta, lista_nombres_imagenes = datos[0], datos[1]
        imagenes_con_nombre = []
        for nombre_imagen in lista_nombres_imagenes:
            imagen_bin = b""
            while True:
                imagen_parte = self.request.recv(1024)
                imagen_bin += imagen_parte
                if len(imagen_parte) < 1024:
                    break
            imagen = pickle.loads(imagen_bin)
            buffer = BytesIO()
            imagen.save(buffer, format='JPEG')
            imagen_bytes = buffer.getvalue()
            img_base64 = base64.b64encode(imagen_bytes)
            img_str = img_base64.decode("utf-8")
            objeto_imagen = ajuste_formato(nombre_imagen, img_str)
            print(f"binario de imagen: {nombre_imagen} recibida")
            self.request.sendall(b"imagen recibida")
            imagenes_con_nombre.append(objeto_imagen)
        self.request.sendall(b"Todas las imagen recibidas, descomprimidas y nombradas")
        respuestas = guardar_imagenes_sino_existe(nombre_carpeta, imagenes_con_nombre)

        for objeto_imagen in imagenes_con_nombre:
            print(objeto_imagen['nombre'])

        for respuesta in respuestas:
            print(respuesta)

        print("fin")
        self.request.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Servidor de procesamiento de imágenes")
    parser.add_argument("-i", "--ip", help="Dirección IP", type=str, default='0.0.0.0')
    parser.add_argument("-p", "--puerto", help="Puerto", type=int, default='5001')
    args = parser.parse_args()

    servidor = ThreadedTCPServer((args.ip, args.puerto), MyTCPHandler)

    with servidor:
        ip, puerto = servidor.server_address
        server_thread = threading.Thread(target=servidor.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print(f"direccion ip {ip} y puerto {puerto}")
        try:
            # Hacer que duerma hasta que  reciba una señal y llamará al manejador apropiado
            signal.pause()
        except:
            # nos permite cerrar el server y liberar el puerto
            servidor.shutdown()
