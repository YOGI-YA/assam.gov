from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.config import settings
import logging

logger = logging.getLogger("govsaarthi.database")

# Primary Database Connection with graceful fallback
# Supports PostgreSQL with pgvector, and falls back seamlessly to SQLite
DATABASE_URL = settings.DATABASE_URL
IS_POSTGRES = DATABASE_URL.startswith("postgresql")

PG_VECTOR_AVAILABLE = False
if IS_POSTGRES:
    try:
        from pgvector.sqlalchemy import Vector
        PG_VECTOR_AVAILABLE = True
    except ImportError:
        PG_VECTOR_AVAILABLE = False

try:
    if IS_POSTGRES:
        # Normalize driver: try postgresql+psycopg2 or postgresql+psycopg for full driver compatibility
        conn_urls = [DATABASE_URL]
        if DATABASE_URL.startswith("postgresql://"):
            conn_urls = [
                DATABASE_URL.replace("postgresql://", "postgresql+psycopg2://", 1),
                DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1),
                DATABASE_URL
            ]

        connected = False
        last_error = None
        for target_url in conn_urls:
            try:
                engine = create_engine(target_url, pool_pre_ping=True)
                with engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    # Attempt to register pgvector extension
                    try:
                        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
                        conn.commit()
                        logger.info("Successfully connected to PostgreSQL and confirmed 'vector' extension.")
                    except Exception as ext_err:
                        logger.warning(f"Note: pgvector extension check: {ext_err}")
                connected = True
                DATABASE_URL = target_url
                break
            except Exception as e:
                last_error = e

        if not connected:
            raise last_error or Exception("Could not connect to PostgreSQL with any driver")
    else:
        # SQLite connection
        engine = create_engine(
            DATABASE_URL, 
            connect_args={"check_same_thread": False}
        )
except Exception as conn_err:
    logger.warning(f"PostgreSQL connection failed ({conn_err}). Falling back to SQLite local database.")
    fallback_url = f"sqlite:///{settings.BASE_DIR / 'govsaarthi.db'}"
    DATABASE_URL = fallback_url
    IS_POSTGRES = False
    PG_VECTOR_AVAILABLE = False
    engine = create_engine(
        fallback_url, 
        connect_args={"check_same_thread": False}
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
