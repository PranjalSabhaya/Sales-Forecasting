FROM python:3.10-slim

WORKDIR /app

# ✅ Install LightGBM dependency
RUN apt-get update && apt-get install -y \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# ✅ Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copy backend code ONLY
COPY backend ./backend
COPY src ./src   

# ✅ Environment
ENV PYTHONUNBUFFERED=1

# ✅ Expose standard port
EXPOSE 8000

# ✅ Correct module path
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "backend.main:app", "--bind", "0.0.0.0:$PORT", "--workers", "2"]