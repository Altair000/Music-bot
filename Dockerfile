# Usa una imagen base que incluya FFmpeg
FROM python:3.10-slim

# Instala FFmpeg
RUN apt-get update && apt-get install -y ffmpeg

# Configura el entorno de trabajo
WORKDIR /app

# Copia los archivos de la aplicación
COPY . .

# Instala dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Ejecuta la aplicación
CMD ["gunicorn", "flask_app:app", "--bind", "0.0.0.0:8080", "--workers", "3"]
