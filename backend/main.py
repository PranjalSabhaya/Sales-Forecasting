import os
from dotenv import load_dotenv

from fastapi import FastAPI,Request
from backend.api.routes import router
from backend.core.model_loader import load_model
from src.utils.download_assets import download_file, validate_parquet
import time

load_dotenv()

app = FastAPI(
    title="Sales Forecasting API",
    version="1.0.1"
)

@app.on_event("startup")
def startup_event():

    print("🚀 Starting application...")

    try:
        model_url = os.getenv("MODEL_URL")
        data_url = os.getenv("DATA_URL")

        model_path = os.getenv("MODEL_PATH")
        data_path = os.getenv("SALES_HISTORY_PATH")

        # 🔽 Download model
        download_file(model_url, model_path)

        # 🔽 Download data
        download_file(data_url, data_path)

        # ✅ Validate parquet
        validate_parquet(data_path)

        # 🔥 Load model
        load_model()

        print("✅ Application ready.")

    except Exception as e:
        print(f"❌ Startup failed: {e}")

@app.middleware("http")
async def log_requests(request: Request, call_next):

    start_time = time.time()

    response = await call_next(request)

    process_time = round(time.time() - start_time, 4)

    print(
        f"{request.method} {request.url.path} "
        f"Status: {response.status_code} "
        f"Time: {process_time}s"
    )

    return response


app.include_router(router)

@app.get("/")
def root():
    return {"message": "Sales Forecast API is running"}

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "sales-forecast-api"
    }
