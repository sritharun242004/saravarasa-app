import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.services.alias_seeder import seed_aliases
from app.routes.onboarding import router as onboarding_router
from app.routes.audit import router as audit_router
from app.routes.challenge import router as challenge_router
from app.routes.compliance import router as compliance_router
from app.routes.reports import router as reports_router
from app.routes.admin import router as admin_router
from app.routes.payment import router as payment_router
from app.routes.foods import router as foods_router
from app.routes.auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    async with AsyncSessionLocal() as db:
        await seed_aliases(db)
    yield


app = FastAPI(
    title="Sarvarasa – 7-Day Wholesome Eating Challenge API",
    description="Food awareness and lifestyle assessment platform",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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


@app.get("/health")
async def health():
    return {"status": "ok", "service": "Sarvarasa Challenge Platform", "version": "1.0.0"}
