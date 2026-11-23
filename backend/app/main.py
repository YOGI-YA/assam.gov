import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import Base, engine, SessionLocal
from app.models.models import User
from app.core.security import hash_password
from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.chat import router as chat_router
from app.api.drafting import router as drafting_router
from app.api.audit import router as audit_router
from app.api.dashboard import router as dashboard_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("govsaarthi")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB tables
    logger.info("Initializing GovSaarthi database schemas...")
    Base.metadata.create_all(bind=engine)

    # Seed default demonstration government officer accounts
    db = SessionLocal()
    try:
        admin_email = "admin@aasc.assam.gov.in"
        if not db.query(User).filter(User.email == admin_email).first():
            admin_user = User(
                id="default-admin-01",
                name="Administrative Officer (AASC)",
                email=admin_email,
                password_hash=hash_password("AssamGov@2026"),
                role="admin",
                department="Assam Administrative Staff College"
            )
            db.add(admin_user)

        officer_email = "officer@dst.assam.gov.in"
        if not db.query(User).filter(User.email == officer_email).first():
            officer_user = User(
                id="default-officer",
                name="Nodal Research Officer (DST/ASSAC)",
                email=officer_email,
                password_hash=hash_password("GovSaarthi@2026"),
                role="officer",
                department="Department of Science & Technology"
            )
            db.add(officer_user)

        db.commit()
        logger.info("Default demonstration user accounts confirmed.")
    except Exception as e:
        logger.error(f"Error seeding demo accounts: {e}")
        db.rollback()
    finally:
        db.close()

    yield
    logger.info("GovSaarthi backend shutdown.")

app = FastAPI(
    title="gov.guide API — Government Knowledge Assistant",
    description="Backend API for Document Intelligence & RAG developed for NESFIC 2026 Challenge (Assam Government)",
    version="1.0.0-MVP",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router, prefix="/api")
app.include_router(documents_router, prefix="/api")
app.include_router(chat_router, prefix="/api")
app.include_router(drafting_router, prefix="/api")
app.include_router(audit_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")

@app.get("/")
def root():
    return {
        "product": "gov.guide",
        "description": "Government Knowledge Assistant — NESFIC 2026 (Assam Government Context)",
        "version": "1.0.0-MVP",
        "status": "Operational",
        "disclaimer": "Demonstration Prototype — Not an officially deployed Assam Government production system."
    }

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "database": "connected",
        "environment": settings.ENVIRONMENT
    }
