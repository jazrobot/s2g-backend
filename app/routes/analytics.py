from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, and_, case
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.session import get_db
from app.models.station import Station, StationStatus
from app.routes.auth import get_current_user

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/stations/status-summary")
async def get_stations_status_summary(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
) -> Dict[str, int]:
    """Get summary of stations by status"""
    result = await db.execute(
        select(Station.status, func.count(Station.id))
        .group_by(Station.status)
    )

    status_counts = {status.value: 0 for status in StationStatus}

    for status, count in result.all():
        status_counts[status.value] = count

    return status_counts


@router.get("/stations/capacity-distribution")
async def get_capacity_distribution(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
    bins: int = Query(
        5, description="Number of capacity ranges to divide into")
) -> List[Dict[str, Any]]:
    """Get distribution of stations by capacity ranges"""
    result = await db.execute(select(Station.max_capacity_kw))
    capacities = [row[0] for row in result.all()]

    if not capacities:
        return []

    min_capacity = min(capacities)
    max_capacity = max(capacities)
    bin_size = (max_capacity - min_capacity) / bins

    distribution = []
    for i in range(bins):
        lower = min_capacity + (i * bin_size)
        upper = lower + bin_size
        count = sum(1 for c in capacities if lower <= c < upper)
        distribution.append({
            "range": f"{lower:.1f} - {upper:.1f} kW",
            "count": count
        })

    return distribution


@router.get("/stations/location-stats")
async def get_location_stats(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """Get statistics by location"""
    result = await db.execute(
        select(
            Station.location,
            func.count(Station.id).label("total_stations"),
            func.avg(Station.max_capacity_kw).label("avg_capacity"),
            func.sum(case((Station.status == StationStatus.ACTIVE, 1), else_=0)).label(
                "active_stations")
        )
        .group_by(Station.location)
    )

    stats = [{
        "location": row.location,
        "total_stations": row.total_stations,
        "avg_capacity": float(row.avg_capacity),
        "active_stations": row.active_stations
    } for row in result.all()]

    return stats


@router.get("/stations/filtered-data")
async def get_filtered_station_data(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(get_current_user),
    status: StationStatus = None,
    min_capacity: float = None,
    max_capacity: float = None,
    location: str = None
) -> List[Dict[str, Any]]:
    """Get filtered station data for interactive charts"""
    query = select(Station)
    filters = []

    if status:
        filters.append(Station.status == status)
    if min_capacity is not None:
        filters.append(Station.max_capacity_kw >= min_capacity)
    if max_capacity is not None:
        filters.append(Station.max_capacity_kw <= max_capacity)
    if location:
        filters.append(Station.location == location)

    if filters:
        query = query.where(and_(*filters))

    result = await db.execute(query)
    stations = result.scalars().all()

    return [{
        "id": str(station.id),
        "name": station.name,
        "location": station.location,
        "max_capacity_kw": station.max_capacity_kw,
        "status": station.status.value
    } for station in stations]
