# Final-Computacion2-TransferenciaImagenes 

## Servidor de Imágenes

Este servidor es una aplicación que permite guardar y procesar imágenes recibidas de clientes en una base de datos MongoDB.

### Funcionamiento General del servidor4, el servidor7 y servidor9

El servidor es capaz de recibir una solicitud de un cliente que incluya el nombre de una carpeta y una lista de nombres de imágenes. Luego, el servidor recibirá las imágenes correspondientes a esos nombres.

Una vez recibidas las imágenes, se realizarán los siguientes procesamientos sobre ellas:

Ajuste de formato: se redimensiona la imagen a un tamaño de 80x90 píxeles y se convierte a escala de grises.
Codificación a base64: se codifica la imagen a formato base64 para su posterior almacenamiento en la base de datos MongoDB.
Finalmente, se almacenarán las imágenes procesadas en la base de datos MongoDB. Si la colección con el nombre de la carpeta no existe en la base de datos, se creará automáticamente. Si ya existe una imagen con el mismo nombre en la colección, se evitará su inserción.

### Diferencia entre el Funcionamiento del Servidor4 y el servidor7
#### El servidor4 

La clase MyTCPHandler es una subclase de socketserver.BaseRequestHandler que se utiliza para manejar la conexión con cada cliente. En su función handle, los datos binarios recibidos se convierten en objetos utilizando pickle. Luego, los nombres de imágenes y las imágenes se separan y se guardan en una lista. Después de recibir todas las imágenes, se llama a una función llamada guardar_imagenes_sino_existe que se encarga de guardar las imágenes en el sistema de archivos.

La clase ThreadedTCPServer es una combinación de socketserver.ThreadingMixIn y socketserver.TCPServer que permite que varios clientes se conecten al servidor simultáneamente.

El código principal se ejecuta en el bloque "if name == "main":" donde se crea el servidor utilizando la clase ThreadedTCPServer y la dirección IP y el puerto especificados por el usuario. Luego, se inicia un hilo para ejecutar el servidor y se muestra la dirección IP y el puerto en el que se está ejecutando. El servidor se detendrá cuando reciba una señal. En caso de error, se llama a la función de apagado para liberar el puerto.

#### El servidor7
El código se trata de un servidor de procesamiento de imágenes, donde se utiliza la biblioteca asyncio para manejar tareas asíncronas y mejorar la eficiencia del servidor. La función principal es "recibir_datos" que es una función asíncrona, identificada por la palabra clave "async def".

El objetivo de la función "recibir_datos" es recibir datos desde un cliente, procesarlos y enviar una respuesta al cliente. Para lograr esto, la función crea tareas usando la función "asyncio.create_task", la cual crea una tarea que se ejecutará de forma asíncrona. Luego, se utiliza "asyncio.gather" para esperar a que la tarea termine y obtener su resultado.

#### El servidor9
Utiliza un sistema de logs y file descriptor para diferenciar la conxion de cada cliente


### Tecnologías utilizadas en ambos servidores

#### asyncio:
Se utiliza para crear aplicaciones en las que varias tareas se ejecutan de manera concurrente y se manejan de manera asíncrona.
#### socketserver:
se utiliza para crear un servidor socket y manejar las conexiones con los clientes.
#### pymongo: 
se utiliza para conectarse y manipular la base de datos MongoDB.
#### PIL (Python Imaging Library):
se utiliza para procesar las imágenes.
#### base64:
se utiliza para codificar las imágenes en formato base64.
#### BytesIO: 
Este objeto es parte del módulo io y se utiliza para trabajar con datos binarios como si fueran un archivo en disco.
#### pickle:
se utiliza para serializar y deserializar los datos enviados entre el servidor y los clientes.
#### argparse:
se utiliza para parsear argumentos en la línea de comandos.
#### threading:
se utiliza para crear hilos y manejar múltiples conexiones simultáneamente.
#### numpy:
Este módulo es una biblioteca de cálculo numérico de alto rendimiento para Python.
#### uuid: 
Este módulo proporciona funciones para generar identificadores únicos en el sistema.
#### logging:
Este módulo permite registrar mensajes de información o de error en un archivo o en la consola, y permite configurar diferentes niveles de log (por ejemplo, solo registrar errores o registrar tanto errores como información).
### Uso

Para utilizar el servidor, es necesario tener MongoDB instalado y en ejecución en la dirección y puerto especificados en la conexión (mongodb://root:root@localhost:27017/).

Para ejecutar el servidor, se debe utilizar el siguiente comando en la línea de comandos:
```bash
python servidor4.py [-h] [-i IP] [-p PUERTO]
python servidor7.py [-h] [-i IP] [-p PUERTO]
```

## Procesamiento de Imágenes Cliente

Este código implementa un cliente que se conecta a un servidor y envía una carpeta de imágenes para su procesamiento. La comunicación entre el cliente y el servidor se realiza a través de sockets y se utiliza el protocolo TCP para asegurar la entrega confiable de los datos.

### Tecnologías utilizadas

Socket: es un mecanismo de comunicación entre procesos que permite la transmisión de datos a través de redes.
argparse: es una librería de Python que facilita la creación de líneas de comandos y la obtención de argumentos.
pickle: es una librería de Python que permite serializar objetos Python en una cadena de bytes y deserializarlos nuevamente.
PIL (Python Imaging Library): es una librería de Python que permite manipular imágenes.

### Cómo funciona
El cliente inicia una conexión con el servidor a través de una dirección IP y un puerto específico. Luego, envia los siguientes datos al servidor:

Nombre de la carpeta que contiene las imágenes.
Lista de nombres de las imágenes en la carpeta.
Una vez que el servidor recibe esta información, le responde al cliente que ha recibido correctamente los datos. Entonces, el cliente comienza a enviar las imágenes una por una y espera una respuesta del servidor después de enviar cada imagen. Finalmente, el cliente envía un mensaje "fin" al servidor para indicar que ha terminado de enviar todas las imágenes y cierra la conexión.


### Tecnologías utilizadas en ambos servidores

#### asyncio:
Se utiliza para crear aplicaciones en las que varias tareas se ejecutan de manera concurrente y se manejan de manera asíncrona.
#### socketserver:
se utiliza para crear un servidor socket y manejar las conexiones con los clientes.
#### pymongo:
se utiliza para conectarse y manipular la base de datos MongoDB.
#### PIL (Python Imaging Library):
se utiliza para procesar las imágenes.
#### base64:
se utiliza para codificar las imágenes en formato base64.
#### pickle:
se utiliza para serializar y deserializar los datos enviados entre el servidor y los clientes.
#### argparse:
se utiliza para parsear argumentos en la línea de comandos.
#### threading:
se utiliza para crear hilos y manejar múltiples conexiones simultáneamente.

### Uso

El cliente se puede ejecutar desde la línea de comandos. Para usarlo, siga estos pasos:

Abra una terminal y diríjase a la carpeta donde se encuentra el código.
Ejecute el siguiente comando:
```bash
python cliente.py [-i IP] [-p PUERTO] [-f CARPETA]
```
. IP: Dirección IP del servidor (opcional, predeterminada a '127.0.0.1').
. PUERTO: Puerto del servidor (opcional, predeterminado a '1234').
. CARPETA: Nombre de la carpeta que contiene las imágenes (opcional, predeterminado a 'img_to_learn').
El cliente se conectará al servidor y comenzará a enviar las imágenes. Los mensajes de respuesta del servidor se imprimirán en la terminal durante
