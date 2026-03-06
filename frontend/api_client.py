import requests


API_URL = "http://127.0.0.1:8000/forecast"


def get_forecast(store_id, item_id, forecast_days):

    payload = {
        "store_id": store_id,
        "item_id": item_id,
        "forecast_days": forecast_days
    }

    try:
        response = requests.post(API_URL, json=payload)

        if response.status_code == 200:
            return response.json()

        return {
            "error": response.json().get("detail", "Unknown error")
        }

    except Exception as e:
        return {
            "error": str(e)
        }