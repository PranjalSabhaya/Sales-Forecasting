from pydantic import BaseModel
from typing import List


class RawPredictionRequest(BaseModel):
    store_id: str
    item_id: str
    date: str
    sales_history: List[float]
