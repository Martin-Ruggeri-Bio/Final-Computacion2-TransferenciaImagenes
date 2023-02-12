#El archivo Dockerfile se construirá a partir de la imagen de Python 3.9
#copia el archivo requirements.txt y los demás archivos del proyecto
#expone el puerto 1234 y ejecuta el archivo server.py con los argumentos de IP y puerto especificados.

# Utilizar un version oficial de Python como imagen base
FROM python:3.9

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copie el archivo de requisitos en el contenedor
COPY requirements.txt /app/requirements.txt
# Copia el código de la aplicación en el contenedor
COPY . /app

# Instalar las dependencias
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
RUN pip freeze > /app/requirements.txt

# Expone el puerto para el servidor
EXPOSE 5000

# Establece el comando que se ejecutará cuando se inicie el contenedor
CMD ["python", "servidor.py"]