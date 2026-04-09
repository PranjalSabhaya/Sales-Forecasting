FROM python:3.10-slim

WORKDIR /app

# ✅ Install only required system dependencies (LightGBM)
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ✅ Copy only dependency file first (for caching)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy ONLY required backend code
COPY backend/main.py ./backend/main.py
COPY backend/api ./backend/api
COPY backend/schemas ./backend/schemas
COPY backend/core ./backend/core
COPY backend/services ./backend/services

RUN mkdir -p models/lightgbm
COPY models/lightgbm/model.pkl ./models/lightgbm/model.pkl

RUN mkdir -p data/backend
COPY data/backend/sales_history.parquet ./data/backend/sales_history.parquet

# Optional (recommended)
ENV PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "backend.main:app", "--bind", "0.0.0.0:8001", "--workers", "2"]