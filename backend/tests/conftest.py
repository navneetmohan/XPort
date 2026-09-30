import datetime
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.db.session import get_db
from app.core.celery_app import celery
from app.models.market_data import MarketData
from app.models.engineered_features import EngineeredFeatures
from app.models.portfolio_recommendation import PortfolioRecommendation
from app.repositories.engineered_features_repository import EngineeredFeaturesRepository
from app.repositories.market_data_repository import MarketDataRepository

# In-memory SQLite engine for test isolation
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Provides a clean in-memory SQLite database session per test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> TestClient:
    """Session test client for FastAPI application with DB dependency override."""
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def configure_celery_eager():
    """Configure Celery to execute tasks synchronously during tests."""
    celery.conf.update(
        task_always_eager=True,
        task_eager_propagates=True,
    )
    yield
    celery.conf.update(
        task_always_eager=False,
        task_eager_propagates=False,
    )


@pytest.fixture
def populated_market_data(db_session):
    """Seed synthetic historical market data and features for 3 assets over 60 trading days."""
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"]
    np.random.seed(100)

    m_repo = MarketDataRepository(db_session)
    f_repo = EngineeredFeaturesRepository(db_session)

    dates = [datetime.date(2026, 1, 1) + datetime.timedelta(days=i) for i in range(60)]

    for sym in symbols:
        m_recs = []
        f_recs = []
        base_price = 1000.0 if "RELIANCE" in sym else (3000.0 if "TCS" in sym else 1500.0)
        price = base_price

        for i, d in enumerate(dates):
            ret = float(np.random.normal(0.0008, 0.012))
            price *= (1.0 + ret)
            vol = int(np.random.randint(50000, 200000))

            m_recs.append({
                "symbol": sym,
                "date": d,
                "open": round(price * 0.998, 2),
                "high": round(price * 1.01, 2),
                "low": round(price * 0.99, 2),
                "close": round(price, 2),
                "adj_close": round(price, 2),
                "volume": vol,
            })

            f_recs.append({
                "symbol": sym,
                "date": d,
                "sma_20": round(price * 0.99, 2),
                "sma_50": round(price * 0.98, 2),
                "ema_20": round(price * 0.995, 2),
                "rsi_14": 52.0,
                "macd": 1.5,
                "macd_signal": 1.2,
                "macd_histogram": 0.3,
                "daily_return": ret,
                "rolling_volatility": 0.015,
            })

        m_repo.upsert_records(m_recs)
        f_repo.upsert_records(f_recs)

    return symbols
