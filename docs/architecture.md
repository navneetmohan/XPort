# XPort: System Architecture & Design Overview

Based on the **XPort Software Requirements Specification (SRS v1.0)** and **Software Design Document (SDD v1.0)**.

## 1. System Vision
XPort is an explainable multi-objective portfolio optimization framework for retail investors. It balances 5 key financial objectives:
1. Expected Return
2. Portfolio Risk (Variance/Volatility)
3. Liquidity
4. Tax Impact
5. Inflation-Adjusted Purchasing Power

Optimization is achieved using the **NSGA-II** evolutionary algorithm subject to investor-specific constraints, and the resulting recommendations are made interpretable via **SHAP** feature attributions and a **rule-based explanation engine**.

## 2. High-Level Architecture
```
                        [ Retail Investor ]
                                │
                                ▼
                       [ Nginx Reverse Proxy ]
                                │
                 ┌──────────────┴──────────────┐
                 ▼                             ▼
        [ React Frontend ]             [ FastAPI Backend ]
       (Vite + TS + Zustand)           (REST API & Gateway)
                                               │
                                       ┌───────┴────────┐
                                       ▼                ▼
                                [ PostgreSQL ]    [ Redis Broker ]
                               (Data Persistence)       │
                                                        ▼
                                                [ Celery Workers ]
                                               (NSGA-II & SHAP Tasks)
```

## 3. Layered Design
- **Presentation Layer (`frontend/`)**: Single-page application built with React, TypeScript, and Vite. Global state managed via Zustand. Centralized API service layer for backend communication.
- **Edge Gateway (`nginx/`)**: Reverse proxy directing `/api/*` to the FastAPI backend and `/*` to the React client.
- **Application & API Layer (`backend/`)**: Built on FastAPI with SQLAlchemy ORM and Alembic migrations. Provides synchronous REST endpoints for profile and session management, while offloading heavy computing jobs.
- **Asynchronous Task Processing**: Celery workers backed by Redis for executing multi-objective genetic algorithms and Shapley value computations outside the HTTP request/response cycle.
- **Data Persistence**: PostgreSQL relational database storing user profiles, historical market features, recommendations, allocations, and explanations.

## 4. Implementation Stages (SDD Section 10)
- **Stage 1 (Current - ~15%)**: Project foundation, monorepo setup, Docker Compose, FastAPI skeleton, React skeleton, Celery/Redis connection, Alembic baseline, and CI scaffolding.
- **Stage 2**: Market data acquisition (Yahoo Finance integration).
- **Stage 3**: Data preprocessing & feature engineering (SMA, EMA, RSI, MACD).
- **Stage 4**: Database integration (Full entity relational schema & CRUD repositories).
- **Stage 5**: Backend services (Auth, User Profile service, Recommendation Orchestrator).
- **Stage 6**: Frontend implementation (Auth flow, Zustand stores, Dashboard).
- **Stage 7**: NSGA-II optimization engine integration.
- **Stage 8**: SHAP explainability engine & rule-based justification.
- **Stage 9**: Historical backtesting, Pareto frontier interactive exploration, and What-if simulator.
- **Stage 10**: System integration.
- **Stage 11**: End-to-end component testing.
- **Stage 12**: Deployment & Prometheus/Grafana monitoring.
