from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from database import create_db_and_tables
from routers import auth, portfolios, investments


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup/shutdown logic."""
    create_db_and_tables()
    yield
    # shutdown logic goes here if needed


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A SaaS API for tracking personal stock investments.",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
# Tighten allowed origins in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(portfolios.router)
app.include_router(investments.router)


# ── Health check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "version": settings.APP_VERSION}
