import numpy as np
from datetime import datetime, timedelta

from app.core.model_loader import get_model
from app.services.history_services import get_sales_history


def build_features(history, current_date):

    history = np.array(history)

    lag_7 = history[-7]
    lag_14 = history[-14]
    lag_28 = history[-28]

    rmean_7 = history[-7:].mean()
    rmean_14 = history[-14:].mean()
    rmean_28 = history[-28:].mean()

    wday = current_date.weekday() + 1
    month = current_date.month
    year = current_date.year

    is_event = 0  # can extend later

    return [
        lag_7, lag_14, lag_28,
        rmean_7, rmean_14, rmean_28,
        wday, month, year, is_event
    ]


def recursive_forecast(store_id, item_id, forecast_days):

    model = get_model()

    if model is None:
        raise ValueError("Model not loaded")

    history = get_sales_history(store_id, item_id)

    if len(history) < 28:
        raise ValueError("Not enough historical data.")

    predictions = []

    current_date = datetime.today()

    for _ in range(forecast_days):

        features = build_features(history, current_date)

        prediction = model.predict([features])[0]

        prediction = float(prediction)

        predictions.append(prediction)

        history.append(prediction)

        current_date += timedelta(days=1)

    return predictions
