import socket
import os
import pickle
import zlib
import argparse
from PIL import Image


def enviar_imagenes(ip, puerto, nombre_carpeta):
    try:
        # Conectarse al servidor
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cliente.connect((ip, puerto))
    except Exception as e:
        print(f"Error al conectar al servidor: {e}")
    try:
        lista_nombres_imagenes = os.listdir(nombre_carpeta)
        # Enviar nombre de la carpeta y cantidad de imágenes
        datos = (nombre_carpeta, lista_nombres_imagenes)
        datos_bin = pickle.dumps(datos)
        cliente.sendall(datos_bin)
    except Exception as e:
        print(f"Error al enviar los datos: {e}")
        cliente.close()
    try:
        # Recibir respuesta del servidor
        respuesta = cliente.recv(1024)
        print(respuesta)
        if respuesta == b"nombre de carpeta y lista nombres imagenes recibidas":
            # Enviar imágenes
            print(os.listdir(nombre_carpeta))
            for imagen in os.listdir(nombre_carpeta):
                ruta_imagen = os.path.join(nombre_carpeta, imagen)
                try:
                    with Image.open(ruta_imagen) as image:
                        cliente.sendall(pickle.dumps(image))
                        respuesta = cliente.recv(1024)
                        print(respuesta)
                except Exception as e:
                    print(f"Error al enviar la imagen {imagen}: {e}")
            respuesta = cliente.recv(1024)
            print(respuesta)
        cliente.sendall(b"fin")
    # Cerrar conexión
    except Exception as e:
        print(f"Error al recibir la respuesta del servidor: {e}")
    finally:
        # Cerrar conexión
        cliente.close()
        print("Conexión cerrada")


# Función principal
if __name__ == "__main__":
    try:
        # Obtiene los argumentos de la línea de comandos
        pars = argparse.ArgumentParser(description="Cliente Procesamiento de imágenes")
        pars.add_argument("-i", "--ip", help="ip", type=str, default='127.0.0.1')
        pars.add_argument("-p", "--puerto", help="Puerto", type=int, default='1234')
        pars.add_argument("-f", "--carpeta", help="Carpeta de imágenes", type=str, default='img_to_learn')
        pars.add_argument("-bz", "--tamaño_buffer", type=int, default='1024')
        args = pars.parse_args()
        # Enviar imágenes desde la carpeta
        enviar_imagenes(args.ip, args.puerto, args.carpeta)
    except Exception as e:
        print("Ocurrió un error: ", e)
    except KeyboardInterrupt:
        print("\nPrograma interrumpido por el usuario")
    finally:
        print("Programa finalizado")
