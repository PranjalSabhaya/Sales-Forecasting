from fastapi import APIRouter, HTTPException

from app.schemas.request_schema import ForecastRequest
from app.services.forecast_service import recursive_forecast

router = APIRouter()

@router.post("/forecast")
def forecast(request: ForecastRequest):
    try:
        predictions = recursive_forecast(
            request.store_id,
            request.item_id,
            request.forecast_days
        )

        return {
            "store_id": request.store_id,
            "item_id": request.item_id,
            "forecast_days": request.forecast_days,
            "forecast": predictions
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
