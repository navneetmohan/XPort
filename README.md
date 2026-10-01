# XPort — Explainable Multi-Objective Portfolio Optimization Framework

> **Current milestone: Functional Market Data & Feature Engineering Pipeline**  
> Stage 1 (Foundation), Stage 2 (Market Data Acquisition), Stage 3 (Data Preprocessing & Feature Engineering), and Stage 4 (Database Schema & Repository Layer) are fully operational and verified.

---

## 1. Overview

**XPort** is an explainable, multi-objective portfolio optimization platform designed for personalized investment planning for retail investors. Traditional portfolio tools often reduce asset allocation to simplistic single-metric trade-offs (such as Markowitz mean-variance optimization) and function as opaque black boxes.

XPort addresses these limitations by:
1. Formulating asset allocation as a **multi-objective optimization problem** using the **NSGA-II** evolutionary algorithm to balance five key financial objectives:
   - Maximizing expected return
   - Minimizing portfolio risk (variance/volatility)
   - Improving liquidity
   - Minimizing tax impact
   - Preserving purchasing power against inflation
2. Rendering **Pareto-optimal solution frontiers** allowing retail investors to explore trade-offs intuitively.
3. Providing **Explainable AI (XAI)** by pairing recommendations with **SHAP** feature-attribution analyses (derived from indicators like SMA, EMA, RSI, MACD) and a **rule-based explanation engine** that translates quantitative scores into plain-language rationale.
4. Supplying a **scheduled data pipeline** driven by Celery Beat and Yahoo Finance with robust data preprocessing, data-quality auditing, and technical indicator engineering persisted in PostgreSQL.

---

## 2. System Architecture

### High-Level Architecture
```
                                [ Retail Investor ]
                                         │
                                         ▼
                               [ Nginx Reverse Proxy ]
                                   (Port 80 Gateway)
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
                 ▼                                               ▼
         [ React Frontend ]                              [ FastAPI Backend ]
       (Vite + TS + Zustand)                            (REST API & Gateway)
                 │                                               │
           (Static / SPA)                                ┌───────┴────────┐
                                                         ▼                ▼
                                                  [ PostgreSQL ]    [ Redis Broker ]
                                                 (Data Storage)      │          │
                                                                     │          │
                                                                     ▼          ▼
                                                             [ Celery Worker ] [ Celery Beat ]
```

### Scheduled Market Data & Feature Pipeline
```
Celery Beat (Periodic Schedule) / FastAPI POST /refresh
                    │
                    ▼
          Market Data Service
                    │
                    ▼
          Yahoo Finance API (OHLCV)
                    │
                    ▼
       Data Preprocessor & Quality Audit
       (Sorting, Deduplication, Bounds, Trading Gap Checks)
                    │
                    ▼
       Feature Engineering Service
       (SMA-20/50, EMA-20/50, Wilder's RSI-14, MACD 12/26/9, Returns, Volatility)
                    │
                    ▼
          PostgreSQL Storage
       (market_data & engineered_features tables)
```

---

## 3. Monorepo Repository Structure

```
XPort/
├── config/
│   └── instruments.yaml          # Curated multi-asset universe configuration
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── health.py           # Health probe endpoint
│   │   │       │   ├── market_data.py      # Market data, status, universe & refresh endpoints
│   │   │       │   ├── features.py         # Engineered features endpoints
│   │   │       │   ├── recommendations.py  # Stage 7 placeholder
│   │   │       │   ├── profiles.py         # Stage 5 placeholder
│   │   │       │   └── whatif.py           # Stage 9 placeholder
│   │   │       └── api.py                  # API v1 router aggregator
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic Settings & environment variables
│   │   │   ├── celery_app.py     # Celery app instance & Beat periodic schedule
│   │   │   ├── instruments.py    # Universe loader, asset class resolution, metadata
│   │   │   ├── swagger_ui.py     # Offline Swagger UI bundle
│   │   │   └── tasks.py          # Background tasks (refresh_market_data_task, health_check)
│   │   ├── db/
│   │   │   ├── base.py           # SQLAlchemy DeclarativeBase
│   │   │   └── session.py        # Engine, SessionLocal, get_db
│   │   ├── models/               # Domain ORM models (MarketData, EngineeredFeatures, etc.)
│   │   ├── repositories/         # Data access repositories (MarketDataRepository, Features)
│   │   ├── schemas/              # Pydantic validation schemas (market data, features, status)
│   │   ├── services/             # Domain business logic (YahooFinance, Preprocessor, Features)
│   │   └── main.py               # FastAPI application entrypoint
│   ├── config/
│   │   └── instruments.yaml      # Backend bundled universe definition
│   ├── migrations/               # Alembic database migration versions (0001 - 0004)
│   ├── tests/                    # Backend unit, indicator & integration test suite
│   ├── alembic.ini               # Database migration config
│   ├── Dockerfile                # Backend container definition
│   ├── pyproject.toml            # Python packaging metadata
│   ├── requirements.txt          # Python dependencies
│   └── .env.example
├── frontend/
│   ├── public/                   # Static assets & icons
│   ├── src/
│   │   ├── components/           # UI components (Navbar, Layout, MarketDataPipelineView)
│   │   ├── pages/                # Views: Dashboard, Login, Profile, etc.
│   │   ├── services/             # API client (marketDataService, healthService)
│   │   ├── stores/               # Zustand state stores (useMarketDataStore, authStore)
│   │   ├── test/                 # Test setup & polyfills
│   │   ├── types/                # Domain TypeScript interfaces (PipelineStatus, MarketData, etc.)
│   │   ├── App.tsx               # Client-side router configuration
│   │   ├── index.css             # Theme tokens & design system styles
│   │   └── main.tsx              # DOM mounting point
│   ├── Dockerfile                # Multi-stage production container
│   ├── nginx.conf                # Frontend SPA Nginx configuration
│   ├── package.json              # NPM dependencies & scripts
│   ├── tsconfig.json             # TypeScript configuration
│   ├── vite.config.ts            # Vite bundler & Vitest configuration
│   └── .env.example
├── nginx/
│   ├── Dockerfile                # Gateway container definition
│   └── nginx.conf                # Reverse proxy routing (/ -> frontend, /api/ -> backend)
├── tests/                        # Infrastructure and docker compose tests
├── docker-compose.yml            # Multi-service local orchestrator (including celery-beat)
├── .env.example                  # Root environment template
└── README.md                     # Project documentation
```

---

## 4. Current Implementation Status vs. Roadmap

| Stage | Milestone | Status in this Release |
| :--- | :--- | :--- |
| **Stage 1** | **Project Foundation** | **COMPLETED**: Monorepo layout, FastAPI skeleton, React+Vite UI, Celery/Redis connection, Alembic setup, Nginx reverse proxy, CI & tests. |
| **Stage 2** | **Market Data Acquisition** | **COMPLETED**: Yahoo Finance service, Curated multi-asset universe configuration (`instruments.yaml`), data validation rules, PostgreSQL bulk upserts, Alembic migration 0002, Celery async task & Beat schedule, market-data API endpoints. |
| **Stage 3** | **Preprocessing & Feature Engineering** | **COMPLETED**: Dedicated `DataPreprocessor` with quality reporting (gaps, OHLC consistency, missing-value sanitization), SMA (20, 50), EMA (20, 50), Wilder's RSI (14), MACD (12, 26, 9), daily return, rolling volatility. Guaranteed no look-ahead data leakage. |
| **Stage 4** | **Database Integration** | **COMPLETED**: SQLAlchemy models (`MarketData`, `EngineeredFeatures`), Alembic migrations `0001` through `0004`, clean repository pattern with bulk upserts, coverage reporting, and symbol/date lookups. |
| **Stage 5** | Backend Services (Profile & Auth) | *Next Phase*: Google OAuth 2.0 sessions, User Profile Service, Recommendation Orchestrator skeleton. |
| **Stage 6** | Frontend Polish & Workflow | *Next Phase*: Interactive portfolio setup, allocation visualizer, and profile editor. |
| **Stage 7** | NSGA-II Optimization | *Planned*: pymoo multi-objective evolutionary optimization engine (5 objectives). |
| **Stage 8** | SHAP Explainability | *Planned*: SHAP feature attribution and rule-based natural language justification. |
| **Stage 9** | Backtesting & What-if | *Planned*: Historical backtest equity curves and side-by-side scenario simulation. |
| **Stage 10** | System Integration | *Planned*: End-to-end integration and smoke verification. |
| **Stage 11** | Verification & UAT | *Planned*: End-user validation across acceptance scenarios. |
| **Stage 12** | Monitoring & Deployment | *Planned*: Prometheus metric scraping and Grafana dashboard provisioning. |

---

## 5. Curated Instrument Universe

Configured in `config/instruments.yaml` and loaded via `app.core.instruments`:

| Category | Symbol | Name | Yahoo Supported | Notes |
| :--- | :--- | :--- | :--- | :--- |
| **Stocks** | `RELIANCE.NS` | Reliance Industries Ltd | Yes | NSE large cap |
| **Stocks** | `TCS.NS` | Tata Consultancy Services Ltd | Yes | NSE large cap |
| **Stocks** | `HDFCBANK.NS` | HDFC Bank Ltd | Yes | NSE banking |
| **Stocks** | `INFY.NS` | Infosys Ltd | Yes | NSE IT |
| **Stocks** | `ICICIBANK.NS` | ICICI Bank Ltd | Yes | NSE banking |
| **Mutual Funds** | `NIFTYBEES.NS` | Nippon India ETF Nifty BeES | Yes | Benchmark index ETF |
| **Mutual Funds** | `JUNIORBEES.NS`| Nippon India ETF Nifty Next 50 | Yes | Next 50 ETF |
| **Gold** | `GOLDBEES.NS` | Nippon India ETF Gold BeES | Yes | Physical Gold ETF |
| **Bonds** | `SETF10GILT.NS`| SBI ETF 10 Year Gilt | Yes | Sovereign 10Y G-Sec ETF |
| **Cash** | `LIQUIDBEES.NS`| Nippon India ETF Liquid BeES | Yes | Daily dividend yield ETF |
| **Cash** | `INR_CASH` | Indian Rupee Cash Reserve | No | Zero-volatility benchmark |

---

## 6. Environment Configuration

Copy the sample environment configuration:
```bash
cp .env.example .env
```

Key configuration variables:
```ini
# Database & Broker
DATABASE_URL=postgresql://xport_user:xport_password@localhost:5432/xport_db
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Market Data & Yahoo Finance
YAHOO_FINANCE_TIMEOUT=15
MARKET_DATA_LOOKBACK_DAYS=730
MARKET_DATA_REFRESH_INTERVAL=86400
MARKET_DATA_INSTRUMENTS_PATH=config/instruments.yaml

# Feature Engineering Parameters
FEATURE_SMA_WINDOWS=20,50
FEATURE_EMA_WINDOWS=20,50
RSI_PERIOD=14
MACD_FAST_PERIOD=12
MACD_SLOW_PERIOD=26
MACD_SIGNAL_PERIOD=9
```

---

## 7. How to Run with Docker Compose

Start all seven services (including Celery Beat):

```bash
docker compose up --build
```

Services started:
- `http://localhost/` — Application via Nginx reverse proxy gateway
- `http://localhost/api/v1/health` — Backend API health check via gateway
- `http://localhost/api/v1/docs` — Interactive OpenAPI / Swagger UI
- `postgres:5432` — PostgreSQL 15 database
- `redis:6379` — Redis cache and Celery message broker
- `celery-worker` — Celery background task worker for async execution
- `celery-beat` — Celery periodic scheduler for market data refresh

To stop all services:
```bash
docker compose down
```

---

## 8. How to Run Locally (Without Docker)

### A. Run Database & Redis
Ensure PostgreSQL and Redis are running on your host machine.
Run database migrations:
```bash
cd backend
alembic upgrade head
```

### B. Run Celery Worker & Celery Beat
In a separate terminal:
```bash
cd backend
celery -A app.core.celery_app.celery worker --loglevel=info
```

In another terminal (for the scheduled refresh):
```bash
cd backend
celery -A app.core.celery_app.celery beat --loglevel=info
```

### C. Run the FastAPI Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```
Navigate to:
- Health: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- Interactive Docs: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)

### D. Run the React Frontend
```bash
cd frontend
npm install
npm run dev
```
Open your browser at [http://localhost:5173](http://localhost:5173). The frontend includes a live pipeline inspector and status view on the Dashboard.

---

## 9. Available API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/api/v1/market-data/status` | Current data pipeline health, record counts, and latest dates per symbol |
| `GET` | `/api/v1/market-data/instruments` | Curated universe list and category metadata |
| `POST`| `/api/v1/market-data/refresh` | Asynchronously trigger market data fetch + cleaning + feature generation |
| `GET` | `/api/v1/market-data/task/{task_id}` | Poll asynchronous Celery pipeline task status |
| `GET` | `/api/v1/market-data/{symbol}` | Paginated raw OHLCV market records with date filtering |
| `GET` | `/api/v1/features/{symbol}` | Paginated engineered features (SMA, EMA, RSI, MACD) |
| `GET` | `/api/v1/health` | Service health status and database connectivity |

### Sample API Responses

#### `GET /api/v1/market-data/status`
```json
{
  "status": "operational",
  "total_universe_instruments": 11,
  "instruments_with_market_data": 10,
  "instruments_with_features": 10,
  "total_market_records": 4820,
  "total_feature_records": 4820,
  "instruments": [
    {
      "symbol": "RELIANCE.NS",
      "name": "Reliance Industries Ltd",
      "asset_class": "stocks",
      "is_yahoo_supported": true,
      "market_data_records": 482,
      "features_records": 482,
      "market_latest_date": "2026-09-30T00:00:00Z",
      "features_latest_date": "2026-09-30T00:00:00Z",
      "has_market_data": true,
      "has_features": true
    }
  ],
  "timestamp": "2026-10-01T07:15:00Z"
}
```

#### `GET /api/v1/features/RELIANCE.NS?limit=2`
```json
{
  "symbol": "RELIANCE.NS",
  "total": 482,
  "page": 1,
  "limit": 2,
  "total_pages": 241,
  "data": [
    {
      "date": "2026-09-30T00:00:00Z",
      "symbol": "RELIANCE.NS",
      "sma_20": 2985.40,
      "sma_50": 2940.15,
      "ema_20": 2990.12,
      "ema_50": 2935.80,
      "rsi_14": 58.42,
      "macd": 18.25,
      "macd_signal": 14.10,
      "macd_histogram": 4.15,
      "daily_return": 0.0085,
      "rolling_volatility": 0.0142
    }
  ]
}
```

---

## 10. How to Run Tests

### Run Backend Tests (Pytest)
```bash
.venv\Scripts\python -m pytest
```
Output: **50 passed** in test suite:
- `test_data_preprocessor.py`: Deduplication, missing values, OHLC sanity bounds, and gap detection.
- `test_feature_indicators.py`: Mathematical correctness of SMA, EMA, Wilder's RSI, MACD, and look-ahead leakage prevention.
- `test_pipeline_endpoints.py`: Market data and feature engineering API routes and schema contracts.
- `test_pipeline_integration.py`: End-to-end integration test (Fetch -> Preprocess -> Feature Engineering -> DB Persistence).
- `test_market_data_service.py` & `test_market_data_repository.py`: Service orchestration and idempotent DB upserts.
- `test_compose_spec.py`: Docker Compose specification validation.

### Run Frontend Tests & Build
```bash
cd frontend
npm test -- --run
npm run build
```
Output: **3 passed** in test suite, clean production build with Vite.

---

## 11. Intentionally NOT Implemented Yet

In accordance with the project roadmap, the following modules are reserved for upcoming milestones:
- Full **NSGA-II multi-objective optimizer** (to be integrated in Stage 7)
- **SHAP explainability engine** and rule-based justification translator (Stage 8)
- Complete **Recommendation Orchestrator** end-to-end recommendation generation (Stage 5 / 7)
- Historical **Backtesting & What-if simulation** engine (Stage 9)
- Production brokerage order execution or real-time tick streaming (Out of project scope)

---

## 12. Security & Ethical AI

- **No Secrets Committed**: All secrets and configurations rely on `.env.example` templates.
- **Ethical AI Notice**: Adhering to SRS Section 9, XPort displays an explicit disclaimer across all views emphasizing that recommendations are decision-support aids, not registered financial advice.
