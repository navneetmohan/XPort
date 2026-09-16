# XPort — Project Status & Progress Report
**Explainable Multi-Objective Portfolio Optimization Framework for Retail Investors**  
**Document Type:** Formal Project Review & Milestone Status Report  
**Current Milestone Completed:** Stage 2: Market Data Acquisition & Ingestion Pipeline (~25% Complete)  
**Date:** September 16, 2026  

---

# SECTION 1: SHOW WHAT EXISTS TODAY

## 1.1 Repository, Package & Folder Structure

XPort is structured as a production-grade, containerized monorepo with strict separation of concerns across presentation, API routing, asynchronous worker pipelines, and relational persistence.

```
XPort/
├── .github/
│   └── workflows/
│       ├── backend.yml                   # GitHub Actions: Python test, lint & flake8 suite
│       └── frontend.yml                  # GitHub Actions: Vite build & Vitest test suite
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── health.py          # Operational health check & Redis/DB ping
│   │   │       │   ├── market_data.py     # OHLCV querying, coverage & Celery sync trigger
│   │   │       │   ├── profiles.py        # Investor profile placeholder (Stage 5)
│   │   │       │   ├── recommendations.py # Optimization & explanation placeholder (Stage 7/8)
│   │   │       │   └── whatif.py          # Scenario simulation placeholder (Stage 9)
│   │   │       └── api.py                 # Central FastAPI v1 router aggregator
│   │   ├── core/
│   │   │   ├── celery_app.py              # Celery instance, broker config & beat schedule
│   │   │   ├── config.py                  # Pydantic Settings with env parsing & validators
│   │   │   └── tasks.py                   # Celery tasks: health_check_task, sync_market_data_task
│   │   ├── db/
│   │   │   ├── base.py                    # SQLAlchemy DeclarativeBase
│   │   │   └── session.py                 # Engine pool, SessionLocal, get_db dependency
│   │   ├── models/
│   │   │   ├── __init__.py                # Model registry
│   │   │   └── market_data.py             # MarketData ORM model (OHLCV + unique constraints)
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   └── market_data_repository.py  # Repository for bulk upsert, filtering & coverage
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── common.py                  # Standard Health & RFC 7807 error models
│   │   │   └── market_data.py             # Pydantic validation & response schemas
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── market_data_service.py     # Orchestrator: Validation rules & persistence
│   │   │   └── yahoo_finance_service.py   # Raw market data acquisition & normalization
│   │   └── main.py                        # FastAPI application entrypoint with CORS & middleware
│   ├── migrations/                        # Alembic database migration environment
│   │   ├── versions/
│   │   │   ├── 0001_initial_baseline.py   # Baseline Alembic version
│   │   │   └── 0002_add_market_data_table.py # DDL for market_data schema & indices
│   │   ├── env.py                         # Migration runner wired to SQLAlchemy Base
│   │   └── script.py.mako
│   ├── tests/                             # Comprehensive pytest test suite (20 backend tests)
│   │   ├── conftest.py                    # Test database fixtures (SQLite in-memory fallback)
│   │   ├── test_api_v1_placeholders.py    # Asserts HTTP 501 contracts for future stages
│   │   ├── test_celery_task.py            # Celery eager task execution tests
│   │   ├── test_health.py                 # API health probe verification
│   │   ├── test_market_data_api.py        # End-to-end API test for market data endpoints
│   │   ├── test_market_data_repository.py # Repository upsert & coverage SQL tests
│   │   ├── test_market_data_service.py    # Data validation rule tests
│   │   └── test_market_data_tasks.py      # Background worker task lifecycle tests
│   ├── alembic.ini                        # Database migration configuration
│   ├── Dockerfile                         # Python 3.10 slim container definition
│   ├── pyproject.toml                     # Python packaging metadata & tool configurations
│   ├── requirements.txt                   # FastAPI, SQLAlchemy, Alembic, Celery, yfinance, etc.
│   └── .env.example
├── frontend/
│   ├── public/                            # Static assets and favicon
│   ├── src/
│   │   ├── components/                    # Reusable React components
│   │   │   ├── Layout.tsx                 # Core shell with ethical disclaimers & container
│   │   │   └── Navbar.tsx                 # Responsive header with live API health status badge
│   │   ├── pages/                         # Core view implementations
│   │   │   ├── Backtesting.tsx            # Historical backtest view with metric cards
│   │   │   ├── Dashboard.tsx              # Executive dashboard with allocation & objective cards
│   │   │   ├── Explainability.tsx         # SHAP attribution & natural language explanation view
│   │   │   ├── Login.tsx                  # User authentication & mock Google OAuth entry
│   │   │   ├── Profile.tsx                # Investor risk profiling & financial goals form
│   │   │   └── WhatIf.tsx                 # Interactive parameter simulation sandbox
│   │   ├── services/
│   │   │   ├── apiClient.ts               # Fetch client with typed error handling
│   │   │   └── healthService.ts           # Polling backend `/api/v1/health`
│   │   ├── stores/                        # Zustand reactive state stores
│   │   │   ├── useAuthStore.ts            # Client session & JWT state
│   │   │   └── useProfileStore.ts         # User financial attributes & risk tolerance state
│   │   ├── test/                          # Frontend test setup & jsdom polyfills
│   │   ├── types/                         # TypeScript domain contracts
│   │   │   └── index.ts                   # Interfaces for recommendations, objectives & profiles
│   │   ├── App.test.tsx                   # Vitest suite testing branding & ethical disclaimers
│   │   ├── App.tsx                        # React Router DOM v6 routing table
│   │   ├── index.css                      # Custom Design System (CSS variables & glassmorphism)
│   │   ├── main.tsx                       # React DOM root mounting script
│   │   └── vite-env.d.ts
│   ├── Dockerfile                         # Multi-stage build (Node build -> Nginx static serving)
│   ├── nginx.conf                         # Client SPA routing & fallback configuration
│   ├── package.json                       # React 18, Vite, TypeScript, Zustand, Lucide-React
│   ├── tsconfig.json                      # Strict TypeScript compilation parameters
│   └── vite.config.ts                     # Bundler settings & local API proxy configuration
├── nginx/
│   ├── Dockerfile                         # Reverse proxy container definition
│   └── nginx.conf                         # Edge routing (`/` to frontend, `/api/` to backend)
├── docs/
│   ├── architecture.md                    # Architecture specification and SDD stage roadmap
│   └── PROJECT_STATUS_REPORT.md           # This formal status document
├── tests/
│   └── test_compose_spec.py               # Infrastructure validation tests (3 tests)
├── docker-compose.yml                     # Multi-service local cluster orchestration (6 services)
├── .env.example                           # Root environment template
├── .gitignore                             # Git ignore rules
├── pytest.ini                             # Pytest discovery settings & flags
└── README.md                              # Complete architectural & operational guide
```

### Technology Stack & Packages
- **Backend API:** FastAPI `0.110.0`, Pydantic `2.6.4`, Pydantic Settings `2.2.1`, Uvicorn `0.28.0`.
- **Data Persistence:** SQLAlchemy `2.0.28`, Alembic `1.13.1`, PostgreSQL 15 (`psycopg2-binary 2.9.9`).
- **Asynchronous Processing:** Celery `5.3.6`, Redis `5.0.3` (message broker and cache).
- **Market Data Engine:** `yfinance 0.2.37`, `pandas 2.2.1`, `numpy 1.26.4`.
- **Frontend SPA:** React `18.2.0`, Vite `5.1.6`, TypeScript `5.2.2`, Zustand `4.5.2`, Lucide React `0.344.0`.
- **Testing & Quality:** Pytest `9.0.3`, pytest-asyncio `1.4.0`, Vitest `1.6.1`, `@testing-library/react 14.2.1`.
- **Containerization & Gateway:** Docker Compose v2, Nginx Alpine (Reverse proxy edge routing).

---

## 1.2 Working UI, API, Database & Model Output

### A. Working User Interface (Frontend SPA)
The frontend application is built on React 18 and TypeScript with a custom-engineered Dark Glassmorphism aesthetic. It is completely wired with responsive layouts, client routing, and global state management:
1. **Application Shell (`Layout.tsx` & `Navbar.tsx`):**
   - Live backend health monitoring indicator querying `/api/v1/health` with real-time status badges (`API Operational` / `Degraded`).
   - Sticky top navigation bar linking to all primary platform workflows.
   - Prominent, ethical AI financial decision-support disclaimer banner displayed across all views in compliance with regulatory expectations.
2. **Interactive Views:**
   - **Dashboard (`Dashboard.tsx`):** Multi-objective trade-off overview, current portfolio summary cards, target allocations, and a live trigger button dispatching optimization requests to the backend API.
   - **Investor Profile (`Profile.tsx`):** Form interface capturing risk tolerance (Conservative, Moderate, Aggressive), investment horizon (1–30 years), liquidity preferences, tax considerations, and capital inputs. Connected to `useProfileStore`.
   - **Explainability View (`Explainability.tsx`):** Structured visual breakdown of SHAP attribution scores and rule-based natural language explanations justifying asset weightings.
   - **What-If Scenario Simulator (`WhatIf.tsx`):** Interactive parameter sliders for testing market shocks (market downturns, inflation spikes, interest rate shifts) against portfolio resilience.
   - **Backtesting Explorer (`Backtesting.tsx`):** Historical performance simulation dashboard comparing multi-objective allocation against benchmark indices (e.g., Nifty 50).
   - **Authentication (`Login.tsx`):** Authentication page supporting mock Google OAuth 2.0 and local credentials with state persistence in `useAuthStore`.

### B. Working API Endpoints
The FastAPI application serves both operational endpoints and explicit RFC 7807/HTTP 501 contracted placeholders for downstream stages:

| HTTP Method | Endpoint Path | Implementation Status | Functional Description |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/health` | **Fully Operational** | Returns JSON system health, version `0.1.0`, environment, and checks connectivity to PostgreSQL and Redis. |
| `GET` | `/api/v1/market-data` | **Fully Operational** | Queries paginated historical OHLCV records with query parameters (`symbol`, `start_date`, `end_date`, `page`, `page_size`). |
| `GET` | `/api/v1/market-data/symbols` | **Fully Operational** | Returns total tracked instruments, record counts, and min/max date coverage per ticker. |
| `POST` | `/api/v1/market-data/sync` | **Fully Operational** | Triggers asynchronous background Celery sync (`sync_market_data_task`) for NSE tickers; returns HTTP 202 Accepted with `task_id`. |
| `POST` | `/api/v1/recommendations` | **Contracted Placeholder** | Returns HTTP 501 Not Implemented (`Stage 7: NSGA-II Optimization`). |
| `GET` | `/api/v1/recommendations/{id}` | **Contracted Placeholder** | Returns HTTP 501 Not Implemented (`Stage 5/7`). |
| `GET` | `/api/v1/recommendations/{id}/explanation` | **Contracted Placeholder** | Returns HTTP 501 Not Implemented (`Stage 8: SHAP Explainability`). |
| `GET` | `/api/v1/recommendations/{id}/backtest` | **Contracted Placeholder** | Returns HTTP 501 Not Implemented (`Stage 9: Backtesting`). |
| `POST` | `/api/v1/profiles` | **Contracted Placeholder** | Returns HTTP 501 Not Implemented (`Stage 4/5: Profiles`). |
| `GET/PUT` | `/api/v1/profiles/{id}` | **Contracted Placeholder** | Returns HTTP 501 Not Implemented (`Stage 5: User Profile Service`). |
| `POST` | `/api/v1/whatif/simulate` | **Contracted Placeholder** | Returns HTTP 501 Not Implemented (`Stage 9: What-If Simulation`). |

### C. Working Database Schema & Migrations
The relational persistence layer is managed via Alembic migrations targeting PostgreSQL:
- **Migration `0001_initial_baseline.py`:** Establishes migration baseline.
- **Migration `0002_add_market_data_table.py`:** Deploys the `market_data` table schema:
  - `id`: Big Integer / Serial Primary Key.
  - `symbol`: VARCHAR(50), indexed, representing the instrument ticker (e.g., `RELIANCE.NS`).
  - `date`: DATE, indexed, representing the trading session.
  - `open`, `high`, `low`, `close`, `adj_close`: NUMERIC(14, 4), validated decimal pricing.
  - `volume`: BIGINT, validated trading volume.
  - `created_at`, `updated_at`: TIMESTAMPTZ, auto-generated audit timestamps.
  - **Constraint:** `uq_market_data_symbol_date` (`UNIQUE(symbol, date)`) preventing duplicate records and enabling idempotent bulk upserts (`ON CONFLICT (symbol, date) DO UPDATE`).

### D. Working Model / Data Pipeline Output
1. **Target Instrument Universe:** Configured for representative Indian equities and ETFs:
   - Equities: `RELIANCE.NS`, `TCS.NS`, `HDFCBANK.NS`, `INFY.NS`, `ICICIBANK.NS`
   - ETFs: `NIFTYBEES.NS` (Equity Index), `GOLDBEES.NS` (Commodity Hedge)
2. **Data Acquisition & Normalization (`YahooFinanceService`):**
   - Fetches historical multi-year OHLCV data via `yfinance`.
   - Cleans multi-index headers, resolves timezones, handles missing/NaN values, and standardizes date representations.
3. **Data Quality Validation Rules (`MarketDataService.validate_record`):**
   - `Rule 1`: Price fields (`open`, `high`, `low`, `close`) must be strictly positive numeric values ($> 0$).
   - `Rule 2`: `volume` must be a non-negative integer ($\ge 0$).
   - `Rule 3`: `high` cannot be lower than `low` ($high \ge low - 0.01$).
   - `Rule 4`: `open` and `close` must lie strictly within the $[low - 0.01, high + 0.01]$ range.
   - Any record failing validation is isolated, logged, and included in the sync summary report.
4. **Automated Celery Beat Schedule:**
   - Celery Beat schedule configured at `0 12 * * 1-5` (12:00 PM UTC Monday–Friday, immediately after the Indian market closing bell) to automatically acquire and sync daily closing bars.

---

## 1.3 Test Suite Execution Results & Logs

All unit, integration, contract, and infrastructure tests pass with zero failures:

### A. Backend & Infrastructure Test Suite (`pytest -v`)
```text
============================= test session starts =============================
platform win32 -- Python 3.10.0, pytest-9.0.3, pluggy-1.6.0
rootdir: Z:\xx\XPort, configfile: pytest.ini
collected 23 items

backend/tests/test_api_v1_placeholders.py::test_recommendations_placeholder PASSED   [  4%]
backend/tests/test_api_v1_placeholders.py::test_recommendations_status_placeholder PASSED [  8%]
backend/tests/test_api_v1_placeholders.py::test_profiles_placeholder PASSED          [ 13%]
backend/tests/test_api_v1_placeholders.py::test_whatif_placeholder PASSED            [ 17%]
backend/tests/test_celery_task.py::test_health_check_task_execution PASSED          [ 21%]
backend/tests/test_health.py::test_root_endpoint PASSED                              [ 26%]
backend/tests/test_health.py::test_health_endpoint PASSED                            [ 30%]
backend/tests/test_health.py::test_root_health_alias PASSED                          [ 34%]
backend/tests/test_market_data_api.py::test_get_market_data_empty PASSED             [ 39%]
backend/tests/test_market_data_api.py::test_get_market_data_with_records PASSED       [ 43%]
backend/tests/test_market_data_api.py::test_get_symbol_coverage_api PASSED          [ 47%]
backend/tests/test_market_data_api.py::test_post_market_data_sync_api PASSED         [ 52%]
backend/tests/test_market_data_repository.py::test_repository_upsert_and_duplicates PASSED [ 56%]
backend/tests/test_market_data_repository.py::test_repository_filtering_and_coverage PASSED [ 60%]
backend/tests/test_market_data_service.py::test_yahoo_finance_service_normalize_dataframe PASSED [ 65%]
backend/tests/test_market_data_service.py::test_yahoo_finance_service_empty_df PASSED [ 69%]
backend/tests/test_market_data_service.py::test_market_data_service_validation_rules PASSED [ 73%]
backend/tests/test_market_data_service.py::test_market_data_service_sync_orchestration PASSED [ 78%]
backend/tests/test_market_data_tasks.py::test_sync_market_data_task_success PASSED   [ 82%]
backend/tests/test_market_data_tasks.py::test_sync_market_data_task_failure_handling PASSED [ 86%]
tests/test_compose_spec.py::test_docker_compose_specification PASSED                 [ 91%]
tests/test_compose_spec.py::test_environment_examples PASSED                         [ 95%]
tests/test_compose_spec.py::test_dockerfiles_exist PASSED                            [100%]

============================= 23 passed in 10.44s =============================
```

### B. Frontend Vitest Test Suite (`npm test -- --run`)
```text
 RUN  v1.6.1 Z:/xx/XPort/frontend

 ✓ src/App.test.tsx (2 tests) 334ms
   ✓ XPort Frontend Foundation > renders application brand and navigation links
   ✓ XPort Frontend Foundation > renders ethical decision-support disclaimer banner

 Test Files  1 passed (1)
      Tests  2 passed (2)
   Duration  36.21s
```

---

## 1.4 One Complete End-to-End Flow Currently Working

### Market Data Synchronization, Validation, Persistence & Retrieval Flow
The entire asynchronous market data lifecycle is operational end-to-end:

```
[ User / Scheduler ]
        │
        ▼  POST /api/v1/market-data/sync (JSON: {"symbols": ["RELIANCE.NS"], "lookback_days": 365})
[ FastAPI Endpoint ] (market_data.py)
        │
        ▼  Dispatches async background task via Redis Broker
[ Celery Queue ] (`sync_market_data_task`)
        │
        ▼  Worker picks up task & initializes isolated DB session
[ MarketDataService ] (market_data_service.py)
        │
        ├─► [ YahooFinanceService ]
        │         │ Fetches raw historical OHLCV data from Yahoo Finance API
        │         ▼ Normalizes DataFrames into standardized record dictionaries
        │
        ├─► [ Validation Pipeline ]
        │         │ Validates: Positive prices, High >= Low, bounds checks, volume >= 0
        │         ▼ Separates valid rows from rejected rows
        │
        ▼
[ MarketDataRepository ] (market_data_repository.py)
        │
        ▼  PostgreSQL Bulk Upsert (`INSERT ... ON CONFLICT (symbol, date) DO UPDATE`)
[ PostgreSQL Database ] (`market_data` table)
        ▲
        │  Query verified records via GET /api/v1/market-data?symbol=RELIANCE.NS
[ Retail Investor / Client ]
```

**Step-by-Step Trace:**
1. **Trigger:** The client issues an HTTP POST request to `/api/v1/market-data/sync` specifying target symbols and lookback duration.
2. **Task Enqueue:** FastAPI validates the payload with `MarketDataSyncRequest` and invokes `sync_market_data_task.delay()`. An HTTP 202 Accepted status is immediately returned to the caller with the unique `task_id`.
3. **Execution:** The Celery worker picks up the job, opens a dedicated SQLAlchemy session, and delegates to `MarketDataService.sync_market_data()`.
4. **Acquisition:** `YahooFinanceService` queries `yfinance` for the symbol universe, handles potential MultiIndex date formats, and transforms data into standardized dictionaries.
5. **Quality Filtering:** Each bar passes through `validate_record()`. Malformed or inverted candles are rejected and logged.
6. **Idempotent Storage:** Valid records are committed to PostgreSQL using `MarketDataRepository.upsert_records()`. Because of the `uq_market_data_symbol_date` unique constraint, duplicate dates are updated without throwing integrity errors.
7. **Client Verification:** The client issues `GET /api/v1/market-data/symbols` or `GET /api/v1/market-data?symbol=RELIANCE.NS&page=1` and receives the verified, stored dataset.

---

# SECTION 2: SHOW WHAT REMAINS

## 2.1 Incomplete Modules and Dependencies

| Module / Layer | Current Status | Missing Components / Dependencies Needed |
| :--- | :--- | :--- |
| **Stage 3: Feature Engineering** | Not Started | Indicator computation module (`app/services/feature_engineering_service.py`). Calculation of SMA (20, 50), EMA (20), RSI (14), MACD (12, 26, 9), and rolling volatility. Dependencies: `pandas-ta` or `ta-lib` / `scipy`. |
| **Stage 4: Domain Database Schema** | Partial (only `market_data` exists) | DDL & SQLAlchemy models for `users`, `investor_profiles`, `portfolio_recommendations`, `allocations`, and `explanations`. Alembic migration `0003_add_domain_entities.py`. |
| **Stage 5: Backend Services & Auth** | Placeholder | Google OAuth 2.0 verification flow, JWT token creation/refresh, `UserProfileService` (CRUD for investor financial preferences), and Recommendation Orchestrator. |
| **Stage 6: Frontend Polish & State Wiring** | Static / Mock UI | Live API integration in `useProfileStore` and `useAuthStore`. Real-time visualization components (Pareto frontier scatter plot and allocation breakdown charts using `recharts` or `chart.js`). |
| **Stage 7: Multi-Objective NSGA-II** | Placeholder | Multi-objective genetic algorithm implementation using `pymoo`. Formulations for 5 financial fitness functions: Expected Return, Risk (Portfolio Volatility), Liquidity, Tax Impact, and Inflation Drag. Cardinality and weight constraints ($\sum w_i = 1$). |
| **Stage 8: SHAP Explainability Engine** | Placeholder | Machine learning explainer using `shap`. TreeExplainer/KernelExplainer for feature importance attribution. Rule-based natural language justification engine mapping quantitative weights to human-readable sentences. |
| **Stage 9: Backtesting & What-If Sandbox** | Placeholder | Vectorized historical portfolio backtesting engine computing CAGR, Sharpe Ratio, Maximum Drawdown, and Sortino Ratio. Scenario simulation engine calculating impact of parameter adjustments. |
| **Stage 12: Production Monitoring** | Scaffolding Only | Prometheus metric exporter (`prometheus-fastapi-instrumentator`), Grafana dashboard provisioning, and Celery Flower task monitoring. |

---

## 2.2 Known Bugs & Technical Blockers

1. **Yahoo Finance Upstream Rate Limiting & Fragility:**
   - *Issue:* `yfinance` relies on scraping public Yahoo Finance endpoints without an enterprise SLA. Rapid consecutive requests during batch runs risk HTTP 429 Too Many Requests or schema parsing failures.
   - *Mitigation Needed:* Implement exponential backoff retries, local Redis caching for intraday queries, and fallback data provider adapters (e.g., Alpha Vantage or NSEpy).
2. **Celery Worker Connection in Standalone Local Testing:**
   - *Issue:* Running pytest without an active Redis instance causes task dispatching to fail unless Celery is explicitly configured in eager mode (`task_always_eager = True`).
   - *Mitigation Needed:* Maintain strict mock/eager testing isolation so developers without local Docker setups can run tests uninterrupted.
3. **Frontend Vitest Warning Regarding Asynchronous State Updates:**
   - *Issue:* Running `npm test` triggers React `act(...)` console warnings due to `Navbar.tsx` polling backend health asynchronously on mount before the test lifecycle terminates.
   - *Mitigation Needed:* Wrap the component mount in React `act()` or mock `healthService.checkHealth()` inside `src/test/setup.ts`.
4. **React Router v7 Deprecation Future Flags:**
   - *Issue:* React Router DOM v6 outputs console warnings for `v7_startTransition` and `v7_relativeSplatPath`.
   - *Mitigation Needed:* Add explicit future flags to `BrowserRouter` in `App.tsx` to ensure seamless upgrade compatibility.

---

## 2.3 Next Measurable Milestone

### Milestone: Stage 3 (Feature Engineering) & Stage 4 (Domain Database Models)
**Target Completion:** End of Next Sprint  
**Target Completion Metric:** ~40% Total Platform Completion  

#### Measurable Acceptance Criteria:
1. **Technical Indicator Pipeline:**
   - Creation of `FeatureEngineeringService` computing 20-day SMA, 50-day SMA, 20-day EMA, 14-day RSI, and MACD (12, 26, 9) signal lines on persisted `market_data` rows.
   - 100% test coverage asserting numerical correctness against standard financial benchmarks.
2. **Database Domain Expansion:**
   - Execution of Alembic migration `0003` creating tables for `users`, `profiles`, `features`, and `recommendations`.
   - Creation of SQLAlchemy ORM models with foreign key cascades and timestamp triggers.
3. **API Expansion:**
   - Exposure of `GET /api/v1/market-data/{symbol}/features` returning calculated indicator series.
   - Operational `POST /api/v1/profiles` and `GET /api/v1/profiles/{id}` saving and reading real investor risk criteria.

---

## 2.4 Student-Wise Immediate Tasks

Based on individual domain specializations and past repository commits:

### 1. Navneet Mohan (Lead Architect / Frontend & Infrastructure)
- [ ] **Frontend Chart Integration:** Install and integrate `recharts` in `Dashboard.tsx` to render dynamic asset allocation donut charts and a preliminary 2D Pareto frontier curve.
- [ ] **State Store API Wiring:** Replace mock storage in `useProfileStore.ts` and `useAuthStore.ts` with live HTTP calls to `/api/v1/profiles` and mock authentication endpoints.
- [ ] **Test & Routing Hardening:**
  - Fix React `act(...)` warning in `App.test.tsx` by mocking `healthService`.
  - Enable React Router v7 future flags in `App.tsx`.
- [ ] **CI/CD Pipeline Enhancement:** Add Docker Compose integration smoke testing step to `.github/workflows/backend.yml`.

### 2. Dhanvin Ranjith (Backend Architecture & Data Pipelines)
- [ ] **Build Feature Engineering Engine (`app/services/feature_engineering_service.py`):**
  - Implement vectorized computations for SMA (20, 50), EMA (20), RSI (14), and MACD using `pandas` and `numpy`.
  - Implement annualized rolling volatility (252 trading days).
- [ ] **Domain Schema Migration (`0003_add_domain_entities.py`):**
  - Create Alembic migration script for `users`, `investor_profiles`, and `engineered_features` tables.
  - Implement corresponding SQLAlchemy models in `app/models/`.
- [ ] **Celery Feature Calculation Task:**
  - Create `calculate_features_task` in `app/core/tasks.py` to trigger after market data synchronization.
- [ ] **Unit Tests:** Write `tests/test_feature_engineering.py` asserting indicator accuracy.

### 3. Fadhi Sulaiman / Fadynextcode24 (Optimization Algorithms & Explainable AI)
- [ ] **NSGA-II Mathematical Modeling (`app/services/optimization/`):**
  - Define the 5 objective mathematical functions using `pymoo`:
    1. Expected Return (mean historical daily return annualized)
    2. Portfolio Variance (quadratic matrix multiplication: $w^T \Sigma w$)
    3. Liquidity Score (volume-weighted turnover)
    4. Tax Impact (short-term vs. long-term asset turnover penalty)
    5. Inflation Drag (purchasing power preservation relative to CPI benchmark)
  - Define asset weight constraint: $\sum_{i=1}^n w_i = 1$ and $0 \le w_i \le 0.35$ (single-asset exposure limit).
- [ ] **SHAP Attribution Prototype (`app/services/explainability/`):**
  - Create feature importance pipeline using `shap.TreeExplainer` on feature indicators.
  - Design rule-based natural language translation templates (e.g., *"Allocated 25% to RELIANCE.NS due to strong 50-day momentum and low downside volatility"*).
- [ ] **Algorithm Baseline Verification:** Develop standalone test scripts verifying Pareto frontier convergence on historical test portfolios.

---
*Report compiled and verified against codebase commit state on September 16, 2026.*
