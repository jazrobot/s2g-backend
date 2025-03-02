import logging
from datetime import datetime
from sqlalchemy import create_engine  # Motor síncrono
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.interval import IntervalTrigger

from app.core.config import settings
from app.models.station import Station, StationStatus
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Convertir la URL asíncrona a una URL síncrona
sync_db_url = str(settings.DATABASE_URL).replace("+asyncpg", "")
sync_engine = create_engine(sync_db_url)

scheduler = AsyncIOScheduler(
    jobstores={
        'default': SQLAlchemyJobStore(engine=sync_engine)
    }
)


async def toggle_station_status():
    """
    Alterna el estado de todas las estaciones de forma asíncrona:
      - Si está ACTIVE, cambia a INACTIVE.
      - Si está INACTIVE, cambia a ACTIVE.
    Además, actualiza last_status_change a la fecha actual (si existe).
    """
    try:
        async with AsyncSessionLocal() as db:
            result = await db.execute(Station.__table__.select())
            stations = result.scalars().all()
            for station in stations:
                if station.status == StationStatus.ACTIVE:
                    station.status = StationStatus.INACTIVE
                else:
                    station.status = StationStatus.ACTIVE
            await db.commit()
            logger.info(f"Toggled status for {len(stations)} stations")
    except Exception as e:
        logger.error(f"Error in scheduled toggle job: {e}")


def start_scheduler(app):
    scheduler.add_job(
        toggle_station_status,
        trigger=IntervalTrigger(minutes=5),
        id="toggle_stations_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Started APScheduler with station status toggle every 5 minutes")
