from pydantic import BaseModel


class ForecastRequest(BaseModel):
    store_id: str
    item_id: str
    forecast_days: int

