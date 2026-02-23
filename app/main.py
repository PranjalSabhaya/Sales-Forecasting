from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(
    title="Sales Forecasting API",
    version="1.0.1"
)

app.include_router(router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "sales-forecast-api"
    }
