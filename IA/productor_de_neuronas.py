from convertidor_images_array import convertidor_imagenes_a_lista_de_array
from neurona_oculta import Neurona
import matplotlib.pyplot as plt

def productor_de_neuronas_ocultas(cant_neuronas_capa_oculta):
    neurona_capa_oculta = []
    for i in range(cant_neuronas_capa_oculta):
        neurona = Neurona(7200)
        neurona_capa_oculta.append(neurona)
    return neurona_capa_oculta

if __name__ == '__main__':
    salida_capa_oculta = []
    url_imagenes_para_aprender = '/home/martin/Facultad/IA/redNeuronal/red_neuronal_imagenes/IA-tP6/images_para_aprender'
    entradas = convertidor_imagenes_a_lista_de_array(url_imagenes_para_aprender)
    salidas_esperadas = [1,0,1,0,1,0,1,0,1,0]
    cant_neuronas_capa_oculta = 100
    cant_iteraciones = 100
    y_salidas_reales_de_cada_imagen = {}
    for key in entradas:
        y_salidas_reales_de_cada_imagen[key]= []
    y_error = []
    x_iteraciones = [i for i in range(cant_iteraciones)]
    neurona_capa_oculta = productor_de_neuronas_ocultas(cant_neuronas_capa_oculta)
    salida_capa_oculta = [0 for i in range(len(neurona_capa_oculta))]
    neurona_final = Neurona(100)
    contador = 0
    delta = 0

    for j in range(cant_iteraciones):
        index_salida = 0
        for key in entradas:
            for i in range(cant_neuronas_capa_oculta):
                neurona_capa_oculta[i].asignar_entrada(entradas[key].copy())
                salida_capa_oculta[i] = neurona_capa_oculta[i].entrenamiento(delta)
            neurona_final.asignar_entrada(salida_capa_oculta.copy())
            neurona_final.salida_esperada = salidas_esperadas[index_salida]
            neurona_final.entrenamiento_back_final()
            delta = neurona_final.delta
            index_salida += 1
            y_salidas_reales_de_cada_imagen[key].append(neurona_final.salida_real)
        y_error.append(neurona_final.error)
        contador += 1
        print(contador)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(21,6))
    for key in y_salidas_reales_de_cada_imagen:
        ax1.plot(x_iteraciones, y_salidas_reales_de_cada_imagen[key],'b', label=key)
    ax1.set_title('Variacion de Salida Real por imagenes en la neurona Final')
    ax1.set_xlabel('Iteraciones')
    ax1.set_ylabel('Salida Real')
    ax2.plot(x_iteraciones, y_error,'g')
    ax2.set_title('Variacion de Error en la neurona Final')
    ax2.set_xlabel('Iteraciones')
    ax2.set_ylabel('Error')
    fig.savefig("Variaciones por Iteraciones.png")

    url_imagenes_para_predecir = '/home/martin/Facultad/IA/redNeuronal/red_neuronal_imagenes/IA-tP6/imagenes_para_predecir'
    entradas2 = convertidor_imagenes_a_lista_de_array(url_imagenes_para_predecir)
    predicciones = {}
    for key in entradas2:
        for i in range(cant_neuronas_capa_oculta):
            neurona_capa_oculta[i].asignar_entrada(entradas2[key].copy())
            salida_capa_oculta[i] = neurona_capa_oculta[i].entrenamiento()
        print(salida_capa_oculta)
        neurona_final.asignar_entrada(salida_capa_oculta.copy())
        salida_real = neurona_final.entrenamiento()
        print(salida_real)
        if abs(1-salida_real) < 0.1 :
            predicciones[key] = 'Persona A'
        else:
            predicciones[key] = 'Persona B'
    
    print("El resultado de las predicciones es:")
    for key in predicciones:
        print(f"Para la imagen: {key}.png la prediccion indica que es la {predicciones[key]}")