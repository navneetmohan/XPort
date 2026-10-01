import json
from typing import List, Optional, Union
from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "XPort Backend API"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "xport-insecure-development-secret-key-change-in-production"

    # PostgreSQL Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/xport_db"

    # Redis & Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Market Data Acquisition Settings
    YAHOO_FINANCE_TIMEOUT: int = 30
    MARKET_DATA_START_DATE: Optional[str] = None
    MARKET_DATA_REFRESH_INTERVAL: int = 86400
    MARKET_DATA_DEFAULT_SYMBOLS: Union[List[str], str] = [
        "RELIANCE.NS",
        "TCS.NS",
        "HDFCBANK.NS",
        "INFY.NS",
        "ICICIBANK.NS",
        "NIFTYBEES.NS",
        "GOLDBEES.NS",
        "SETF10GILT.NS",
        "LIQUIDBEES.NS",
    ]
    MARKET_DATA_DEFAULT_LOOKBACK_DAYS: int = 1825
    MARKET_DATA_SYNC_CRON: str = "0 12 * * 1-5"

    # Feature Engineering Settings
    FEATURE_SMA_WINDOWS: Union[List[int], str] = [20, 50]
    FEATURE_EMA_WINDOWS: Union[List[int], str] = [20, 50]
    RSI_PERIOD: int = 14
    MACD_FAST_PERIOD: int = 12
    MACD_SLOW_PERIOD: int = 26
    MACD_SIGNAL_PERIOD: int = 9

    # CORS configuration
    BACKEND_CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost",
        "http://localhost:80",
        "http://localhost:3000",
        "http://localhost:5173",
    ]

    @field_validator("MARKET_DATA_DEFAULT_SYMBOLS", mode="before")
    @classmethod
    def assemble_market_data_symbols(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, str) and v.startswith("["):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except Exception:
                pass
        return v if isinstance(v, list) else []

    @field_validator("FEATURE_SMA_WINDOWS", "FEATURE_EMA_WINDOWS", mode="before")
    @classmethod
    def assemble_int_list(cls, v: Union[str, List[int]]) -> List[int]:
        if isinstance(v, str) and not v.startswith("["):
            return [int(i.strip()) for i in v.split(",") if i.strip().isdigit()]
        elif isinstance(v, str) and v.startswith("["):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [int(item) for item in parsed]
            except Exception:
                pass
        return v if isinstance(v, list) else []

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, str) and v.startswith("["):
            try:
                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return [str(item) for item in parsed]
            except Exception:
                pass
        return v if isinstance(v, list) else []

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


settings = Settings()
