import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

logger = logging.getLogger(__name__)

def _init_engine():
    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql"):
        try:
            # Test PostgreSQL connectivity with a short timeout
            test_engine = create_engine(
                db_url,
                connect_args={"connect_timeout": 2},
                pool_pre_ping=True,
                pool_recycle=3600,
            )
            with test_engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            logger.info("Connected to PostgreSQL database.")
            return test_engine
        except Exception as exc:
            logger.warning(
                f"PostgreSQL connection to {db_url} failed ({exc}). "
                "Falling back to local SQLite database (sqlite:///./xport_local.db) for standalone development."
            )
            fallback_engine = create_engine(
                "sqlite:///./xport_local.db",
                connect_args={"check_same_thread": False},
            )
            try:
                from app.db.base import Base
                import app.models  # noqa: F401
                Base.metadata.create_all(bind=fallback_engine)
                logger.info("Initialized local SQLite schema successfully.")
            except Exception as schema_err:
                logger.error(f"Failed to auto-create SQLite schema: {schema_err}")
            return fallback_engine
    elif db_url.startswith("sqlite"):
        sqlite_engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False},
        )
        try:
            from app.db.base import Base
            import app.models  # noqa: F401
            Base.metadata.create_all(bind=sqlite_engine)
        except Exception:
            pass
        return sqlite_engine
    else:
        return create_engine(db_url, pool_pre_ping=True, pool_recycle=3600)


engine = _init_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency for obtaining a SQLAlchemy session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Helper to check database reachability for health checks."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning(f"Database health check probe failed: {exc}")
        return False
