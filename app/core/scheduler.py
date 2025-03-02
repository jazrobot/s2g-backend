import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.future import select
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore

from app.core.config import settings
from app.models.station import Station, StationStatus
from app.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Create a synchronous engine for the job store (remove "+asyncpg" if present)
sync_db_url = str(settings.DATABASE_URL).replace("+asyncpg", "")
sync_engine = create_engine(sync_db_url)

# Global scheduler instance
scheduler = AsyncIOScheduler(
    timezone="UTC",
    jobstores={
        'default': SQLAlchemyJobStore(engine=sync_engine)
    }
)


async def scheduled_status_change(station_id: str, target_status: str):
    """Change the status of a station after a delay."""
    try:
        async with AsyncSessionLocal() as db:
            print(
                f"Changing status of station {station_id} to {target_status}")
            result = await db.execute(select(Station).where(Station.id == station_id))
            station = result.scalars().first()
            if station:
                station.status = StationStatus(target_status)
                await db.commit()
                logger.info(
                    f"Station {station_id} status changed to {target_status}")
            else:
                logger.error(f"Station {station_id} not found")
    except Exception as e:
        logger.error(f"Error changing status: {e}")
