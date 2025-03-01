from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import oauth, auth
from app.core.config import settings
from app.core.scheduler import start_scheduler
from app.db.session import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create a connection to the database and start the scheduler
    db = next(get_db())
    app.state.db = db
    start_scheduler(app)
    yield
    # Shutdown: close the connection to the database
    if hasattr(app.state, "db"):
        app.state.db.close()

app = FastAPI(
    title="Charging Stations API",
    description="API for managing electric vehicle charging stations",
    version="1.0.0",
    lifespan=lifespan
)

# Configuración de CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin)
                       for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Incluye las rutas
app.include_router(auth.router)
app.include_router(oauth.router)
# Próximamente se implementará stations.router


@app.get("/")
async def root():
    return {"message": "Welcome to the Charging Stations API"}


@app.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}
