import numpy as np
from datetime import datetime
from fastapi import HTTPException


def build_features_from_raw(data: dict):

    history = data["sales_history"]

    if len(history) < 28:
        raise HTTPException(
            status_code=400,
            detail="At least 28 historical sales values are required."
        )

    history = np.array(history)

    lag_7 = history[-7]
    lag_14 = history[-14]
    lag_28 = history[-28]

    rmean_7 = history[-7:].mean()
    rmean_14 = history[-14:].mean()
    rmean_28 = history[-28:].mean()

    date_obj = datetime.strptime(data["date"], "%Y-%m-%d")

    wday = date_obj.weekday() + 1
    month = date_obj.month
    year = date_obj.year

    is_event = 0

    return {
        "lag_7": lag_7,
        "lag_14": lag_14,
        "lag_28": lag_28,
        "rmean_7": rmean_7,
        "rmean_14": rmean_14,
        "rmean_28": rmean_28,
        "wday": wday,
        "month": month,
        "year": year,
        "is_event": is_event
    }
