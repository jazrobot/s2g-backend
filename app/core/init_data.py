from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.station import Station, StationStatus

# Datos de muestra para las estaciones de carga
sample_stations = [
    {
        "name": "Estación Zócalo",
        "location": "Ciudad de México Centro",
        "max_capacity_kw": 150.0,
        "status": StationStatus.ACTIVE
    },
    {
        "name": "Estación San Pedro",
        "location": "Monterrey Norte",
        "max_capacity_kw": 100.0,
        "status": StationStatus.ACTIVE
    },
    {
        "name": "Estación Chapultepec",
        "location": "Ciudad de México Oeste",
        "max_capacity_kw": 75.0,
        "status": StationStatus.INACTIVE
    },
    {
        "name": "Estación Zapopan",
        "location": "Guadalajara Centro",
        "max_capacity_kw": 200.0,
        "status": StationStatus.INACTIVE
    },
    {
        "name": "Estación Zona Hotelera",
        "location": "Cancún Centro",
        "max_capacity_kw": 120.0,
        "status": StationStatus.ACTIVE
    },
    {
        "name": "Estación Reforma",
        "location": "Ciudad de México Centro",
        "max_capacity_kw": 180.0,
        "status": StationStatus.ACTIVE
    },
    {
        "name": "Estación Valle",
        "location": "Monterrey Norte",
        "max_capacity_kw": 250.0,
        "status": StationStatus.ACTIVE
    },
    {
        "name": "Estación Revolución",
        "location": "Tijuana Centro",
        "max_capacity_kw": 90.0,
        "status": StationStatus.INACTIVE
    },
    {
        "name": "Estación Terminal 2",
        "location": "Ciudad de México Centro",
        "max_capacity_kw": 300.0,
        "status": StationStatus.ACTIVE
    },
    {
        "name": "Estación Tecnológico",
        "location": "Monterrey Norte",
        "max_capacity_kw": 50.0,
        "status": StationStatus.INACTIVE
    }
]


async def init_sample_data(db: AsyncSession) -> None:
    """Inicializa la base de datos con datos de muestra, evitando duplicados"""
    for station_data in sample_stations:
        # Verificar si ya existe una estación con el mismo nombre y ubicación
        result = await db.execute(
            select(Station).where(
                Station.name == station_data["name"],
                Station.location == station_data["location"]
            )
        )
        existing_station = result.scalars().first()

        if not existing_station:
            # Crear nueva estación solo si no existe
            station = Station(
                name=station_data["name"],
                location=station_data["location"],
                max_capacity_kw=station_data["max_capacity_kw"],
                status=station_data["status"]
            )
            db.add(station)

    await db.commit()
