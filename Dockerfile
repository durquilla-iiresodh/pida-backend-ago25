# Usa una imagen base de Python oficial y ligera. Python 3.12 es una excelente opción estable para producción.
FROM python:3.12-slim

# Establece el directorio de trabajo dentro del contenedor.
# Todas las acciones siguientes ocurrirán dentro de /app.
WORKDIR /app

# Copia solo el archivo de requerimientos primero para aprovechar el caché de capas de Docker.
# Si no cambias tus dependencias, Docker no necesitará reinstalarlas en cada build.
COPY requirements.txt .

# Instala las dependencias.
RUN pip install --no-cache-dir -r requirements.txt

# Ahora, copia todo el código de tu aplicación (la carpeta 'src' y cualquier otro archivo).
COPY ./src ./src

# Expone el puerto en el que Uvicorn se ejecutará. Cloud Run usará esta información.
# El valor por defecto es 8080.
EXPOSE 8080

# El comando para iniciar la aplicación.
# Esta es la línea clave que soluciona tu problema.
# "src.main:app" le dice a Uvicorn: "dentro de la carpeta 'src', busca el archivo 'main.py' y dentro de él, el objeto llamado 'app'".
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080"]