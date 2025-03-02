from datetime import datetime, timedelta
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.station import Station
from app.schemas.station import StationCreate, Station as StationSchema, StationUpdate, StationStatusUpdate, StationScheduledStatusChange
from app.routes.auth import get_current_user

from app.core.scheduler import scheduler, scheduled_status_change

router = APIRouter(prefix="/stations", tags=["stations"])


@router.get("/", response_model=List[StationSchema])
async def get_stations(db: AsyncSession = Depends(get_db)):
    """Get all charging stations"""
    result = await db.execute(select(Station))
    stations = result.scalars().all()
    return stations


@router.post("/", response_model=StationSchema)
async def create_station(
    *,
    db: AsyncSession = Depends(get_db),
    station_in: StationCreate,
    _: dict = Depends(get_current_user)
):
    """Create a new charging station"""
    station = Station(
        name=station_in.name,
        location=station_in.location,
        max_capacity_kw=station_in.max_capacity_kw
    )
    db.add(station)
    await db.commit()
    await db.refresh(station)
    return station


@router.patch("/{station_id}", response_model=StationSchema)
async def update_station(
    *,
    db: AsyncSession = Depends(get_db),
    station_id: str,
    station_in: StationUpdate,
    _: dict = Depends(get_current_user)
):
    """Update a charging station"""
    result = await db.execute(select(Station).where(Station.id == station_id))
    station = result.scalars().first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    for field, value in station_in.dict(exclude_unset=True).items():
        setattr(station, field, value)

    await db.commit()
    await db.refresh(station)
    return station


@router.patch("/{station_id}/status", response_model=StationSchema)
async def update_station_status(
    *,
    db: AsyncSession = Depends(get_db),
    station_id: str,
    status_in: StationStatusUpdate,
    _: dict = Depends(get_current_user)
):
    """Update a station's status"""
    result = await db.execute(select(Station).where(Station.id == station_id))
    station = result.scalars().first()

    if not station:
        raise HTTPException(status_code=404, detail="Station not found")

    station.status = status_in.status
    await db.commit()
    await db.refresh(station)
    return station


@router.post("/{station_id}/schedule-status-change")
async def schedule_status_change(
    station_id: str,
    status_change: StationScheduledStatusChange,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
):
    # Validate station exists
    result = await db.execute(select(Station).where(Station.id == station_id))
    station = result.scalars().first()
    if not station:
        raise HTTPException(status_code=404, detail="Station not found")
    run_date = datetime.utcnow() + timedelta(seconds=status_change.delay_seconds)
    print(f"run_date: {run_date}")
    job = scheduler.add_job(
        scheduled_status_change,
        trigger="date",
        run_date=run_date,
        args=[station_id, status_change.status],
        id=f"change_status_{station_id}_{run_date.timestamp()}",
        replace_existing=True
    )

    return {
        "job_id": job.id,
        "scheduled_run": run_date.isoformat(),
        "message": f"Status change for station {station_id} scheduled to {status_change.status}"
    }
