
# StockTrader

Full-stack stock and option prediction & paper-trading platform built with **FastAPI**, **Angular + TypeScript**, **LightGBM + XGBoost + LSTM ensemble**, **PostgreSQL**, and **Redis**.

## Repository Structure

```
├── backend/
│   ├── api/                        # FastAPI app, routers, schemas
│   │   └── routers/                # health, predict, model, backtest, trade, admin, paper, stream
│   ├── prediction_engine/
│   │   ├── data_pipeline/          # Yahoo/NSE/IV/news connectors, validation
│   │   ├── feature_store/          # Feature transforms, selection, versioned store
│   │   ├── models/                 # BaseModel, LightGBM, XGBoost, LSTM, Ensemble
│   │   ├── training/              # Trainer with walk-forward splits + ensemble
│   │   ├── backtest/              # Backtester engine
│   │   └── monitoring/           # Drift detection (KS/PSI), canary deployment
│   ├── trading_engine/            # Order manager (equity + options), Angel adapter
│   ├── paper_trading/             # Paper accounts, executor, replayer
│   ├── services/                  # Model manager, registry, monitoring, MLflow, Celery
│   ├── db/                        # SQLAlchemy models & session config
│   ├── tests/                     # pytest test suite
│   └── scripts/                   # Client example scripts
├── frontend/
│   ├── src/
│   │   ├── pages/                 # PaperDashboard, PaperAccountDetail, SignalExplorer, SignalDetail, LiveChart
│   │   ├── components/            # EquityChart, LivePriceChart, OrderIntentForm, SimulationSummaryCard
│   │   └── services/             # paperApi, predictionApi, priceStream
│   └── e2e/                      # E2E tests
├── models/                       # Model artifacts and registry
├── storage/                      # Raw data, backtest results
├── infra/                        # K8s, Helm, Grafana dashboards + alerts
├── docs/                         # API spec, features, model card, runbooks
├── docker-compose.dev.yml        # Dev: API + Frontend + Postgres + Redis + Celery
├── docker-compose.prod.yml       # Staging/Prod compose
├── Dockerfile
├── requirements.txt
└── .github/workflows/            # CI (backend + frontend) and CD (build + deploy)
```

## Features

- **Multi-model ensemble**: LightGBM + XGBoost + LSTM with stacked meta-learner and isotonic calibration
- **Option trading**: CE/PE signals, Greeks estimation, IV surfaces, vertical spreads, iron condors, covered calls
- **Paper trading**: ₹100,000 default accounts, simulated fills with slippage, day/range replay
- **SHAP explainability**: Top-5 feature contributions per prediction
- **Live streaming**: WebSocket + SSE price feeds with reconnection
- **Drift detection**: KS test + PSI on features and labels with alerting
- **Canary deployment**: Shadow inference → A/B evaluation → promotion rules
- **MLflow integration**: Model versioning, metrics tracking, artifact storage
- **Scheduled retrain**: Celery-based nightly retrain with retrain gating

## Prerequisites

- **Python 3.14+**
- **Node.js 22+** (for frontend)
- **Docker & Docker Compose** (for containerised dev)

## Quick Start

### 1. Clone & configure environment variables

```bash
cp .env.example .env        # edit values as needed
```

### 2a. Run with Docker (recommended)

```bash
docker-compose -f docker-compose.dev.yml up --build
```

- Backend API: **http://localhost:8000** (Swagger: `/docs`)
- Frontend: **http://localhost:3000**

### 2b. Run locally (without Docker)

```bash
# Backend
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
uvicorn backend.api.main:app --reload

# Frontend
cd frontend
npm install
npm start
```

### 3. Verify

```bash
curl http://localhost:8000/api/v1/health
# {"status":"ok"}
```

## Running Tests

```bash
pytest backend/tests/ -v
```

## Linting

```bash
flake8 backend/ --max-line-length 120
```

## API Endpoints

All endpoints live under `/api/v1`.

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/predict` | Single-ticker equity prediction |
| POST | `/predict/options` | Option signal with Greeks |
| POST | `/batch_predict` | Multi-ticker batch prediction |
| GET | `/model/status` | Current model info |
| POST | `/model/reload` | Hot-reload a model version |
| POST | `/backtest/run` | Launch a backtest job |
| GET | `/backtest/{job_id}/results` | Retrieve backtest results |
| POST | `/trade_intent` | Generate trading intent (equity + options) |
| POST | `/execute` | Execute an order (paper/live) |
| POST | `/paper/accounts` | Create paper account (₹100,000 default) |
| GET | `/paper/accounts` | List paper accounts |
| GET | `/paper/{id}/equity` | Get equity curve |
| GET | `/paper/{id}/metrics` | Get account metrics |
| POST | `/paper/{id}/order_intent` | Submit order intent |
| POST | `/paper/{id}/replay` | Run day replay |
| WS | `/stream/price/{symbol}` | Live price WebSocket |
| GET | `/stream/price/{symbol}` | Live price SSE fallback |
| POST | `/retrain` | Trigger model retraining |
| GET | `/metrics` | Prometheus metrics export |
| GET | `/registry/versions` | List model versions |
| GET | `/registry/mlflow` | MLflow model metadata |
| POST | `/drift/check` | Run drift detection |
| GET | `/canary/status` | Canary deployment status |

See [docs/api_spec.md](docs/api_spec.md) for full request/response schemas.

## Training Pipeline

```bash
# 1. Download sample data (50 NSE tickers, 1 year)
python -m scripts.sample_data.download_sample

# 2. Train the baseline LightGBM model
python -m backend.prediction_engine.training.trainer
```

The trainer uses walk-forward cross-validation (60/20/20 split) and saves artifacts to `models/artifacts/`.

## CI/CD

- **CI** (`.github/workflows/ci.yml`): flake8 lint + pytest on every push/PR to `main`
- **CD** (`.github/workflows/cd.yml`): Docker build → push → deploy to staging on merge to `main`

## Deployment

```bash
# Development
docker-compose -f docker-compose.dev.yml up --build

# Production
docker-compose -f docker-compose.prod.yml up -d

# Kubernetes
kubectl apply -f infra/k8s/

# Helm
helm install stocktrader infra/helm/stocktrader/
```

See [docs/runbooks.md](docs/runbooks.md) for operational procedures.

## Developer Guide

| Area | Location | Notes |
|------|----------|-------|
| Add an endpoint | `backend/api/routers/` | Create router, include in `main.py` |
| Add a schema | `backend/api/schemas.py` | Pydantic `BaseModel` |
| Add a feature | `backend/prediction_engine/feature_store/transforms.py` | Pure function, register in `FEATURE_COLUMNS` |
| Add a DB model | `backend/db/models.py` | SQLAlchemy declarative with `Base` |
| Add a service | `backend/services/` | Import into routers |
| Add a test | `backend/tests/` | Prefix with `test_`, use `client` fixture |

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | Postgres connection string | SQLite fallback |
| `REDIS_URL` | Redis connection string | `redis://redis:6379/0` |
| `ALLOWED_ORIGINS` | Comma-separated CORS origins | `*` |
| `SECRET_KEY` | App secret key | — |
| `APP_ENV` | `development` / `production` | `development` |
| `PAPER_MODE` | Enable paper trading | `true` |
| `MLFLOW_TRACKING_URI` | MLflow server URL | `mlruns` |
| `SENTRY_DSN` | Sentry error monitoring DSN | — |
| `CELERY_BROKER_URL` | Celery broker (Redis) | `redis://localhost:6379/1` |
