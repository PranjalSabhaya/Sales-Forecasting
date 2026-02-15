from fastapi import APIRouter
from app.schemas.request_schema import RawPredictionRequest
from app.services.prediction_service import make_prediction

router = APIRouter()


@router.post("/predict")
def predict(request: RawPredictionRequest):

    prediction = make_prediction(request.dict())

    return {
        "prediction": prediction
    }
