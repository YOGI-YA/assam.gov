import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory for backend
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env if present
env_path = BASE_DIR / ".env"
if not env_path.exists():
    env_path = BASE_DIR.parent / ".env"
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

class Settings:
    PROJECT_NAME: str = "gov.guide"
    PROJECT_VERSION: str = "1.0.0-MVP"
    BASE_DIR: Path = BASE_DIR
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "govsaarthi-nesfic2026-secret-key-change-in-prod-secure-32chars")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))

    # Database
    # Primary: PostgreSQL with pgvector. Fallback: SQLite
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{BASE_DIR / 'govsaarthi.db'}"
    )

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq") # groq, gemini, openai, local-rag
    LLM_API_KEY: str = os.getenv("LLM_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "openai/gpt-oss-120b")

    # Embeddings
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local")
    EMBEDDING_DIMENSION: int = 384

    # Storage
    UPLOAD_DIR: Path = Path(os.getenv("UPLOAD_DIR", str(BASE_DIR / "uploads")))
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "25"))

    # RAG Settings
    RELEVANCE_SIMILARITY_THRESHOLD: float = float(os.getenv("RELEVANCE_SIMILARITY_THRESHOLD", "0.20"))
    TOP_K_CHUNKS: int = int(os.getenv("TOP_K_CHUNKS", "7"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "700"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

settings = Settings()
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
