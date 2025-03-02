from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import oauth, auth, stations
from app.core.config import settings

from app.core.scheduler import scheduler

prefix = "/api/v1"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: start the scheduler
    scheduler.start()
    yield
    # Shutdown: shut down the scheduler
    scheduler.shutdown()

app = FastAPI(
    title="Charging Stations API",
    description="API for managing electric vehicle charging stations",
    version="1.0.0",
    lifespan=lifespan,
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth.router, prefix=prefix)
app.include_router(oauth.router, prefix=prefix)
app.include_router(stations.router, prefix=prefix)


@app.get("/")
async def root():
    return {"message": "Welcome to the Charging Stations API"}


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
