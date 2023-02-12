import socket
import os
import pickle
import zlib
import argparse
from PIL import Image


def enviar_imagenes(ip, puerto, nombre_carpeta):
    # Conectarse al servidor
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip, puerto))
    lista_nombres_imagenes = os.listdir(nombre_carpeta)
    # Enviar nombre de la carpeta y cantidad de imágenes
    datos = (nombre_carpeta, lista_nombres_imagenes)
    datos_bin = pickle.dumps(datos)
    cliente.sendall(datos_bin)

    # Recibir respuesta del servidor
    respuesta = cliente.recv(1024)
    print(respuesta)
    if respuesta == b"nombre de carpeta y lista nombres imagenes recibidas":
        # Enviar imágenes
        print(os.listdir(nombre_carpeta))
        for imagen in os.listdir(nombre_carpeta):
            ruta_imagen = os.path.join(nombre_carpeta, imagen)
            # with open(ruta_imagen, "rb") as img:
            #     imagen = img.read()
            #     imagen_comprimida = zlib.compress(imagen)
            #     cliente.sendall(imagen_comprimida)
            with Image.open(ruta_imagen) as image:
                cliente.sendall(pickle.dumps(image))
                respuesta = cliente.recv(1024)
                print(respuesta)
        respuesta = cliente.recv(1024)
        print(respuesta)
    cliente.sendall(b"fin")
    # Cerrar conexión
    cliente.close()


# Función principal
if __name__ == "__main__":
    # Obtiene los argumentos de la línea de comandos
    pars = argparse.ArgumentParser(description="Cliente Procesamiento de imágenes")
    pars.add_argument("-i", "--ip", help="ip", type=str, default='127.0.0.1')
    pars.add_argument("-p", "--puerto", help="Puerto", type=int, default='1234')
    pars.add_argument("-f", "--carpeta", help="Carpeta de imágenes", type=str, default='img_to_learn')
    pars.add_argument("-bz", "--tamaño_buffer", type=int, default='1024')
    args = pars.parse_args()
    # Enviar imágenes desde la carpeta
    enviar_imagenes(args.ip, args.puerto, args.carpeta)