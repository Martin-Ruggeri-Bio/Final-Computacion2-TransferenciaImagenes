import redis
import time

# Inicializar conexión a Redis
conn = redis.StrictRedis(host='localhost', port=6379, db=0)

# Definir las funciones a ejecutar en segundo plano
def funcion_1(n):
    print(f'Ejecutando funcion 1 con n = {n}')
    time.sleep(5)
    return n * n

def funcion_2(n):
    print(f'Ejecutando funcion 2 con n = {n}')
    time.sleep(3)
    return n + n

# Función principal que ejecuta funciones en segundo plano
def ejecutar_funciones_en_segundo_plano(n):
    # Enviar las funciones a ejecutar en segundo plano a Redis
    job_1 = conn.rpush('jobs', 'funcion_1')
    job_2 = conn.rpush('jobs', 'funcion_2')

    # Esperar hasta que las tareas estén completas
    while conn.llen('jobs') > 0:
        time.sleep(0.5)

    # Obtener los resultados de las funciones
    resultado_1 = conn.get(f'resultado_funcion_1_{job_1}')
    resultado_2 = conn.get(f'resultado_funcion_2_{job_2}')

    print(f'Resultados: funcion_1 = {resultado_1}, funcion_2 = {resultado_2}')


if __name__ == "__main__":
    # Verificar que la conexión sea exitosa
    try:
        conn.ping()
        print("Conexión exitosa a Redis")
    except redis.exceptions.ConnectionError:
        print("Error de conexión a Redis")
    ejecutar_funciones_en_segundo_plano(5)