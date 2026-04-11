<div align="center">

# 📈 ForecastFlow

**End-to-end retail sales forecasting — from raw data ingestion to a live REST API.**

[![LightGBM](https://img.shields.io/badge/Model-LightGBM-3de8a0?style=flat-square&logo=python&logoColor=white)](https://lightgbm.readthedocs.io/)
[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-a78fff?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![Streamlit](https://img.shields.io/badge/Frontend-Streamlit-60b4f9?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Docker](https://img.shields.io/badge/Deploy-Docker-f97060?style=flat-square&logo=docker&logoColor=white)](https://www.docker.com/)

| Forecast Horizon | Lag Windows | Feature Types | API Endpoint |
|:-:|:-:|:-:|:-:|
| **28 days** | **3** | **7** | **1** |

</div>

---

## Overview

ForecastFlow is a production-style machine learning system for predicting future retail sales at the store–item level using historical time-series data.

```
Streamlit UI  →  FastAPI Backend  →  LightGBM Model
  (Frontend)         (API)            (ML Core)
```

The system covers the full ML lifecycle: data ingestion, memory-efficient feature engineering, model training, API-based inference, and an interactive frontend — all containerized with Docker.

---

## Features

| Feature | Details |
|---|---|
| **Time-Series Forecasting** | Predicts future sales using historical demand |
| **Lag & Rolling Features** | 7, 14, and 28-day windows for temporal patterns |
| **Recursive Multi-Step Forecast** | Each prediction feeds back into the next step |
| **Production REST API** | FastAPI with `/forecast`, `/health`, and request logging |
| **Interactive UI** | Streamlit app for real-time predictions |
| **Memory Optimization** | Chunk-based processing for large datasets |
| **Modular Pipelines** | Clean separation of ingestion, features, training, inference |
| **Docker Ready** | Containerized backend and frontend |

---

## Model

**Algorithm:** LightGBM Regressor

**Features:**

```
Lag Features      →  lag_7, lag_14, lag_28
Rolling Means     →  rmean_7, rmean_14, rmean_28
Time Features     →  wday, month, year
Event Feature     →  is_event
```

**Forecast Strategy:** Recursive forecasting — predicts one step, feeds the result back, and repeats for a **28-day horizon**.

---

## Project Structure

```
Sales-Forecasting/
├── backend/                        # FastAPI backend
│   ├── main.py                     # App entry point
│   ├── api/
│   │   └── routes.py               # API route handlers
│   ├── core/
│   │   └── model_loader.py         # Model loading logic
│   ├── schemas/
│   │   └── request_schema.py       # Pydantic request/response models
│   └── services/
│       ├── forecast_service.py     # Forecast logic
│       └── history_services.py     # Sales history helpers
│
├── frontend/                       # Streamlit UI
│   ├── app.py
│   ├── api_client.py
│   ├── Dockerfile
│   └── requirements.txt
│
├── src/                            # ML pipelines
│   ├── pipelines/
│   │   ├── data_ingestion.py
│   │   ├── feature_engineering.py
│   │   ├── training_pipeline.py
│   │   └── inference_pipeline.py
│   └── utils/
│       ├── config_loader.py
│       ├── data_validation.py
│       ├── download_assets.py
│       ├── experiment_logger.py
│       └── prepare_backend_data.py
│
├── data/
│   ├── raw/                        # Source CSVs (calendar, sales, prices)
│   ├── interim/                    # Intermediate long-format data
│   ├── processed/                  # Feature-engineered train data & results
│   │   ├── baselines/
│   │   └── ml_results/
│   ├── predictions/                # Forecast output
│   └── backend/                    # Parquet data served by API
│
├── models/
│   └── lightgbm/
│       ├── model.pkl
│       ├── metadata.json
│       └── feature_importance.csv
│
├── notebooks/                      # Exploration & analysis
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_cleaning.ipynb
│   ├── 03_eda.ipynb
│   ├── 04_feature_engineering.ipynb
│   ├── 05_baseline_models.ipynb
│   ├── 05b_classical_baselines.ipynb
│   ├── 06_prediction_models.ipynb
│   └── 07_final_results.ipynb
│
├── config/
│   ├── local.yaml
│   └── prod.yaml
│
├── entrypoints/
│   ├── train.py
│   └── inference.py
│
├── experiments/
│   └── experiment_log.csv
│
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## API Reference

### `GET /health`

```json
{
  "status": "healthy",
  "service": "sales-forecast-api"
}
```

### `POST /forecast`

**Request:**
```json
{
  "store_id": "CA_1",
  "item_id": "FOODS_1_001",
  "sales_history": [10, 12, 11, 13, "..."]
}
```

**Response:**
```json
{
  "predictions": [12.3, 13.1, 14.0, "..."]
}
```

> Full interactive API docs available at `http://127.0.0.1:8000/docs` once the backend is running.

---

## Dataset

This project uses the **M5 Forecasting — Accuracy** dataset from Kaggle, which contains hierarchical sales data from Walmart across 3 US states and 3 product categories.

> **[Download the data from Kaggle](https://www.kaggle.com/competitions/m5-forecasting-accuracy/data)**

Once downloaded, place the CSV files into `data/raw/`:

```
data/raw/
├── calendar.csv
├── sales_train_evaluation.csv
├── sales_train_validation.csv
├── sell_prices.csv
└── sample_submission.csv
```

---

## Getting Started

### Local Setup

```bash
git clone <repo-url>
cd Sales-Forecasting
pip install -r requirements.txt
```

### Prepare the Data

```bash
# Run the full training pipeline
python entrypoints/train.py

# Prepare backend data (required before running the API)
python src/utils/prepare_backend_data.py
```

### Run the Backend

```bash
uvicorn backend.main:app --reload
```

### Run the Frontend

```bash
cd frontend
streamlit run app.py
```

### Run with Docker

```bash
docker-compose up --build
```

---

## Pipeline Flow

```
Raw Data
   ↓  Data Ingestion
   ↓  Feature Engineering
   ↓  LightGBM Training
   ↓  Model Saved
   ↓  Inference Pipeline
   ↓  API → Frontend
```

---

## Handling Large Files

The model artifact and sales history data are too large for the repo and are hosted on Google Drive.

| File | Description | Link |
|---|---|---|
| `model.pkl` | Trained LightGBM model | [Download](https://drive.google.com/file/d/1QxJOm5AcNj39NvWDJJsqCVAEK8gxixNu/view) |
| `sales_history.parquet` | Processed sales history for API | [Download](https://drive.google.com/file/d/1I3IHgtW3xgTTrdZQrnwByhHC7ZN91bZh/view) |

## Tech Stack

| Layer | Technology |
|---|---|
| **Model** | LightGBM · NumPy · Pandas |
| **Backend** | FastAPI · Uvicorn · Pydantic |
| **Frontend** | Streamlit |
| **Data Processing** | Pandas · PyArrow |
| **Containerization** | Docker |
| **Storage** | Google Drive (runtime download via gdown) |


---

## Key Learnings

Working on this project involved building production-style ML pipelines, handling large-scale time-series data with memory constraints, designing scalable REST APIs, and integrating machine learning with a full backend and frontend — including debugging real-world deployment issues.

---

<div align="center">

Built by **Pranjal Sabhaya**

</div>
