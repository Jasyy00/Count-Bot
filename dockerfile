# Python 3.11 als Base Image
FROM python:3.11-slim

# Arbeitsverzeichnis erstellen
WORKDIR /app

# Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Bot-Code kopieren
COPY main.py .

# Port für Health Check
EXPOSE 8080

# Umgebungsvariable für Python
ENV PYTHONUNBUFFERED=1

# Bot starten
CMD ["python", "main.py"]
