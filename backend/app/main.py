import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

logger = logging.getLogger("uvicorn.error")

from app.config import settings
from app.core.rate_limit import limiter
from app.database import init_db, AsyncSessionLocal
from app.services.alias_seeder import seed_aliases
from app.routes.onboarding import router as onboarding_router
from app.routes.audit_routes import router as audit_router
from app.routes.challenge import router as challenge_router
from app.routes.compliance import router as compliance_router
from app.routes.reports import router as reports_router
from app.routes.admin import router as admin_router
from app.routes.payment import router as payment_router
from app.routes.foods import router as foods_router
from app.routes.auth import router as auth_router
from app.routes.profile import router as profile_router
from app.routes.tests import router as tests_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with AsyncSessionLocal() as db:
        await seed_aliases(db)
    yield


_is_dev = settings.environment.lower() == "development"

# A wildcard origin combined with allow_credentials=True lets any site make
# credentialed requests (Starlette echoes the request's Origin header back
# verbatim in that combination instead of literally sending "*") — refuse to
# boot rather than silently open this up via a misconfigured env var.
if "*" in settings.cors_origins:
    raise RuntimeError(
        "CORS_ORIGINS must not contain '*' — allow_credentials=True makes a "
        "wildcard origin a same-origin-policy bypass. List explicit origins."
    )

app = FastAPI(
    title="Sarvarasa – 7-Day Wholesome Eating Challenge API",
    description="Food awareness and lifestyle assessment platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if _is_dev else None,
    redoc_url="/redoc" if _is_dev else None,
    openapi_url="/openapi.json" if _is_dev else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    # Without this, an unhandled exception is caught by Starlette's outermost
    # ServerErrorMiddleware (above CORSMiddleware), so the resulting 500 has no
    # CORS headers — the browser reports it as a blocked CORS request instead
    # of a real error, and the client never sees a status code or message.
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Something went wrong. Please try again."},
    )

# Serve uploaded meal images
os.makedirs(settings.upload_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

app.include_router(onboarding_router)
app.include_router(audit_router)
app.include_router(challenge_router)
app.include_router(compliance_router)
app.include_router(reports_router)
app.include_router(admin_router)
app.include_router(payment_router)
app.include_router(foods_router)
app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(tests_router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Sarvarasa Challenge Platform", "version": "1.0.0"}
