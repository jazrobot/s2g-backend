from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.interval import IntervalTrigger
import logging

from app.core.config import settings
from app.models.station import Station, StationStatus
from app.db.session import SessionLocal

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(
    jobstores={
        'default': SQLAlchemyJobStore(url=settings.DATABASE_URL)
    }
)


def toggle_station_status():
    db = SessionLocal()
    try:
        # Seleccionar todas las estaciones
        stations = db.query(Station).all()
        for station in stations:
            if station.status == StationStatus.ACTIVE:
                station.status = StationStatus.INACTIVE
            else:
                station.status = StationStatus.ACTIVE
        db.commit()
        logger.info(f"Toggled status for {len(stations)} stations")
    except Exception as e:
        logger.error(f"Error in scheduled toggle job: {e}")
        db.rollback()
    finally:
        db.close()


def start_scheduler(app):
    scheduler.add_job(
        toggle_station_status,
        trigger=IntervalTrigger(minutes=5),
        id="toggle_stations_job",
        replace_existing=True,
    )
    scheduler.start()
    logger.info("Started APScheduler with station status toggle every 5 minutes")
