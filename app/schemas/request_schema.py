from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    store_id: str
    item_id: str
    forecast_days: int = Field(
        ...,
        ge=1,
        le=28,
        description="Number of days to forecast (1 to 28)"
    )

