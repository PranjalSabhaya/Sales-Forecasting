from fastapi import FastAPI,Request
from app.api.routes import router
import time

app = FastAPI(
    title="Sales Forecasting API",
    version="1.0.1"
)

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


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "sales-forecast-api"
    }
