# XPort Infrastructure

This directory contains infrastructure configuration templates, deployment manifests, and operational specifications for XPort.

## Structure (Evolution Across Stages)

- `docker/`: Dockerfiles and base image configurations
- `monitoring/`: Prometheus and Grafana alerting, dashboard definitions, and scrape targets (Planned for Stage 12)
- `k8s/` or `compose/`: Environment-specific orchestration overrides (e.g., staging, production)

## Current Stage (Stage 1 Foundation)
At the foundation stage (~15%), local container orchestration is driven by the root `docker-compose.yml`, which orchestrates:
1. PostgreSQL 15 database
2. Redis 7 cache and message broker
3. FastAPI application server
4. Celery worker process
5. React + Vite frontend client
6. Nginx reverse proxy gateway
