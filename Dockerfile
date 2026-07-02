FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" "python", "app.py"]

# Exponer el puerto 5000 para que podamos acceder desde el navegador
EXPOSE 5000

