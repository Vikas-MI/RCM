from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    assistant,
    availity,
    claims,
    dashboard,
    documents,
    ehr,
    eligibility,
    encounters,
    fhir,
    health,
    insurance,
    patients,
    payers,
    policy,
)
from app.core.config import get_settings
from app.core.database import Base, engine
from app.core.logging import configure_logging, get_logger
import app.models  # noqa: F401 — register metadata for create_all

configure_logging()
logger = get_logger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(_app: FastAPI):
    logger.info("Starting %s (%s)", settings.app_name, settings.app_env)
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as exc:  # noqa: BLE001
        logger.warning("create_all skipped/failed: %s", exc)
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Smart RCM POC — Mock Epic/Oracle EHR + PostgreSQL + Mock Availity eligibility. "
        "NOT live Epic, Oracle Health, or Availity."
    ),
    version="0.4.0-poc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")
app.include_router(patients.router, prefix="/api")
app.include_router(encounters.router, prefix="/api")
app.include_router(insurance.router, prefix="/api")
app.include_router(payers.router, prefix="/api")
app.include_router(eligibility.router, prefix="/api")
app.include_router(fhir.router, prefix="/api")
app.include_router(ehr.router, prefix="/api")
app.include_router(availity.router, prefix="/api")
app.include_router(documents.router, prefix="/api")
app.include_router(policy.router, prefix="/api")
app.include_router(claims.router, prefix="/api")
app.include_router(assistant.router, prefix="/api")
