FROM python:3.10-slim

WORKDIR /app

COPY frontend/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY frontend/ .

EXPOSE 8502

CMD ["streamlit", "run", "app.py","--server.port=8502","--server.address=0.0.0.0"]