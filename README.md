# XPort — Explainable Multi-Objective Portfolio Optimization Framework

> **Status: Stage 1 Foundation (~15% Complete)**  
> This repository represents the **initial foundational architecture** of XPort. Core infrastructure, service skeletons, API contracts, and testing pipelines are established, while domain-heavy algorithmic modules (NSGA-II, SHAP, Yahoo Finance data pipelines) are scheduled for subsequent stages.

---

## 1. Overview

**XPort** is an explainable, multi-objective portfolio optimization platform designed for retail investors. Traditional portfolio tools often reduce asset allocation to a simplistic, single-metric trade-off (such as Markowitz mean-variance optimization) and function as opaque black boxes. 

XPort addresses these limitations by:
1. Formulating asset allocation as a **multi-objective optimization problem** using the **NSGA-II** evolutionary algorithm to balance five key financial objectives:
   - Maximizing expected return
   - Minimizing portfolio risk (variance/volatility)
   - Improving liquidity
   - Minimizing tax impact
   - Preserving purchasing power against inflation
2. Rendering **Pareto-optimal solution frontiers** to allow retail investors to explore trade-offs intuitively.
3. Providing **Explainable AI (XAI)** by pairing recommendations with **SHAP** feature-attribution analyses (derived from indicators like SMA, EMA, RSI, MACD) and a **rule-based explanation engine** that converts quantitative scores into plain-language rationale.

---

## 2. High-Level Architecture

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
                                                 (Data Storage)          │
                                                                         ▼
                                                                 [ Celery Workers ]
                                                                (Async NSGA-II & SHAP)
```

---

## 3. Monorepo Repository Structure

```
XPort/
├── .github/
│   └── workflows/
│       ├── backend.yml           # Python test and lint workflow
│       └── frontend.yml          # Node/React build and test workflow
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── health.py           # Health probe endpoint
│   │   │       │   ├── recommendations.py  # Stage 7 placeholder
│   │   │       │   ├── profiles.py         # Stage 5 placeholder
│   │   │       │   └── whatif.py           # Stage 9 placeholder
│   │   │       └── api.py                  # API v1 router aggregator
│   │   ├── core/
│   │   │   ├── config.py         # Pydantic Settings
│   │   │   ├── celery_app.py     # Celery app instance
│   │   │   └── tasks.py          # Foundation health_check_task
│   │   ├── db/
│   │   │   ├── base.py           # SQLAlchemy DeclarativeBase
│   │   │   └── session.py        # Engine, SessionLocal, get_db
│   │   ├── models/               # Domain ORM models (Stage 4)
│   │   ├── repositories/         # Data access repositories (Stage 4)
│   │   ├── schemas/              # Pydantic validation schemas
│   │   │   └── common.py
│   │   ├── services/             # Domain business logic (Stage 5+)
│   │   └── main.py               # FastAPI application entrypoint
│   ├── migrations/               # Alembic database migration scripts
│   ├── tests/                    # Backend unit & integration test suite
│   ├── alembic.ini               # Database migration config
│   ├── Dockerfile                # Backend container definition
│   ├── pyproject.toml            # Python packaging metadata
│   ├── requirements.txt          # Python dependencies
│   └── .env.example
├── frontend/
│   ├── public/                   # Static assets & icons
│   ├── src/
│   │   ├── components/           # Reusable UI components (Navbar, Layout)
│   │   ├── pages/                # Views: Dashboard, Login, Profile, etc.
│   │   ├── services/             # API client & health services
│   │   ├── stores/               # Zustand state stores (Auth, Profile)
│   │   ├── test/                 # Test setup & polyfills
│   │   ├── types/                # Domain TypeScript interfaces
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
├── infrastructure/               # Future IaC and monitoring manifests
├── docs/                         # Specifications and architecture docs
├── tests/                        # Infrastructure and docker compose tests
├── docker-compose.yml            # Multi-service local orchestrator
├── .env.example                  # Root environment template
├── .gitignore                    # Git ignore patterns
└── README.md                     # Project documentation
```

---

## 4. Current Implementation Status vs. Upcoming Roadmap

As defined in Section 10 of the Software Design Document (SDD), development follows a phased, verified roadmap:

| Stage | Milestone | Status in this Release |
| :--- | :--- | :--- |
| **Stage 1** | **Project Foundation (~15%)** | **COMPLETED**: Monorepo layout, FastAPI skeleton, React+Vite UI, Celery/Redis connection, Alembic setup, Nginx reverse proxy, CI & tests. |
| **Stage 2** | Market Data Acquisition | *Next Phase*: Yahoo Finance API integration, OHLCV ingestion. |
| **Stage 3** | Feature Engineering | *Planned*: Computation of SMA, EMA, RSI, and MACD indicators. |
| **Stage 4** | Database Integration | *Planned*: Full domain schema (User, Profile, MarketData, Recommendations, Allocations). |
| **Stage 5** | Backend Services | *Planned*: Google OAuth 2.0 sessions, User Profile Service, Recommendation Orchestrator. |
| **Stage 6** | Frontend Polish | *Planned*: Interactive state bindings, charts, and API polling integration. |
| **Stage 7** | NSGA-II Optimization | *Planned*: pymoo multi-objective evolutionary optimization engine. |
| **Stage 8** | SHAP Explainability | *Planned*: SHAP feature attribution and rule-based natural language justification. |
| **Stage 9** | Backtesting & What-if | *Planned*: Historical backtest equity curves and side-by-side scenario simulation. |
| **Stage 10** | System Integration | *Planned*: End-to-end integration and smoke verification. |
| **Stage 11** | Verification & UAT | *Planned*: End-user validation across acceptance scenarios. |
| **Stage 12** | Monitoring & Deployment | *Planned*: Prometheus metric scraping and Grafana dashboard provisioning. |

---

## 5. Prerequisites

- **Node.js**: v18.0+ (v20+ recommended)
- **Python**: v3.10+
- **Docker & Docker Compose**: (Recommended for full multi-container execution)

---

## 6. Environment Setup

Copy the sample environment configuration:
```bash
cp .env.example .env
```

Defaults are configured for local development:
- Backend runs on `http://localhost:8000`
- Frontend runs on `http://localhost:5173` (Vite dev) or `http://localhost:3000` (Docker)
- Edge Nginx Gateway runs on `http://localhost:80`
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`

---

## 7. How to Run with Docker Compose

When Docker is available on your machine, start all six foundation services with:

```bash
docker compose up --build
```

Services started:
- `http://localhost/` — Application via Nginx reverse proxy gateway
- `http://localhost/api/v1/health` — Backend API health check via gateway
- `http://localhost/api/v1/docs` — Interactive OpenAPI / Swagger UI
- `postgres:5432` — PostgreSQL 15 database
- `redis:6379` — Redis cache and Celery message broker
- `celery-worker` — Celery background task worker

To stop all services:
```bash
docker compose down
```

---

## 8. How to Run Locally (Without Docker)

### A. Run the Backend
1. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   # macOS/Linux:
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```bash
   pip install -r backend/requirements.txt
   ```
3. Start the FastAPI development server:
   ```bash
   cd backend
   uvicorn app.main:app --reload --port 8000
   ```
4. Verify backend health:
   Navigate to [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health) or [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs).

### B. Run the Frontend
1. Open a new terminal and navigate to the `frontend/` directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser at [http://localhost:5173](http://localhost:5173). The frontend includes a live proxy forwarding `/api` calls directly to the local FastAPI backend.

---

## 9. How to Run Tests

### Run Backend Tests (Pytest)
```bash
pytest backend/tests
```
Tests include:
- `test_health.py`: Verifies `/api/v1/health` status codes, version tags, and environment data.
- `test_api_v1_placeholders.py`: Asserts HTTP 501 Not Implemented contracts for `/recommendations`, `/profiles`, and `/whatif`.
- `test_celery_task.py`: Exercises `health_check_task` directly in Celery eager mode.

### Run Infrastructure & Docker Compose Validation Tests
```bash
pytest tests/test_compose_spec.py
```
Validates:
- All 6 container definitions in `docker-compose.yml`
- Healthcheck commands and intervals
- Volume persistence and internal networks
- Environment templates

### Run Frontend Tests & Build
```bash
cd frontend
npm test
npm run build
```
Validates:
- Component rendering (brand, navigation, disclaimer banners)
- TypeScript strict type checking and asset bundling

---

## 10. Security & Ethical AI

- **No Secrets Committed**: All configuration relies on `.env.example` templates.
- **Ethical AI Notice**: Adhering to SRS Section 9, XPort displays an explicit disclaimer across all views emphasizing that recommendations are decision-support aids, not registered financial advice.
