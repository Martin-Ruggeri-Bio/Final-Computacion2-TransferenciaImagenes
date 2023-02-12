#Importar librería cv2
import cv2
import os


def convertidor_imagenes_a_lista_de_array(url):
  contenido = os.listdir(url)
  contenido = sorted (contenido)
  vectores_de_imagenes = {}
  for nombre in contenido:
    url_file = url + '/' + nombre
    img = cv2.imread(url_file,0).flatten().tolist()
    vector = [img[i]/1000 for i in range(0, len(img))]
    vectores_de_imagenes[nombre[0:7]] = vector
  return vectores_de_imagenes

if __name__ == '__main__':
  entradas = convertidor_imagenes_a_lista_de_array('/home/martin/Facultad/IA/redNeuronal/red_neuronal_imagenes/images_para_aprender')
  print(entradas.keys())
