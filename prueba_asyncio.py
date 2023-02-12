import asyncio
import time

# Definir las funciones a ejecutar en segundo plano
async def funcion_1(n):
    print(f'Ejecutando funcion 1 con n = {n}')
    await asyncio.sleep(5)
    return n * n

async def funcion_2(n):
    print(f'Ejecutando funcion 2 con n = {n}')
    await asyncio.sleep(3)
    return n + n

# Función principal que ejecuta funciones en segundo plano
async def ejecutar_funciones_en_segundo_plano(n):
    # Ejecutar las funciones en segundo plano usando asyncio
    resultado_1 = asyncio.create_task(funcion_1(n))
    resultado_2 = asyncio.create_task(funcion_2(n))

    # Esperar hasta que las tareas estén completas
    await asyncio.gather(resultado_1, resultado_2)

    # Obtener los resultados de las funciones
    resultado_1 = resultado_1.result()
    resultado_2 = resultado_2.result()

    print(f'Resultados: funcion_1 = {resultado_1}, funcion_2 = {resultado_2}')

if __name__ == "__main__":
    # Inicializar el event loop de asyncio
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ejecutar_funciones_en_segundo_plano(5))
    loop.close()