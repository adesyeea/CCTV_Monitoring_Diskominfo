"""
Vehicle / items endpoint — routes that expose vehicle data from CCTV.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.schemas.item import (
    VehicleSimple,
    VehicleSummary,
    VehiclePerCCTV,
    VehicleHourly,
    VehicleRealtime,
)
from app.services import vehicle_service

router = APIRouter(prefix="/vehicles", tags=["Vehicles"])


@router.get("", response_model=List[VehicleSimple])
def get_all_data(db: Session = Depends(get_db)):
    """Ambil semua data kendaraan (100 terbaru)."""
    return vehicle_service.get_all_vehicles(db)


@router.get("/masuk", response_model=List[VehicleSummary])
def kendaraan_masuk(db: Session = Depends(get_db)):
    """Total kendaraan masuk (direction = 1)."""
    return vehicle_service.get_vehicles_masuk(db)


@router.get("/keluar", response_model=List[VehicleSummary])
def kendaraan_keluar(db: Session = Depends(get_db)):
    """Total kendaraan keluar (direction = 2)."""
    return vehicle_service.get_vehicles_keluar(db)


@router.get("/today", response_model=List[VehicleSummary])
def kendaraan_hari_ini(db: Session = Depends(get_db)):
    """Data kendaraan hari ini."""
    return vehicle_service.get_vehicles_today(db)


@router.get("/cctv", response_model=List[VehiclePerCCTV])
def kendaraan_per_cctv(db: Session = Depends(get_db)):
    """Data kendaraan per CCTV (device_id)."""
    return vehicle_service.get_vehicles_per_cctv(db)


@router.get("/hourly", response_model=List[VehicleHourly])
def kendaraan_per_jam(db: Session = Depends(get_db)):
    """Data kendaraan per jam."""
    return vehicle_service.get_vehicles_hourly(db)


@router.get("/realtime", response_model=List[VehicleRealtime])
def realtime(db: Session = Depends(get_db)):
    """Data realtime — 10 deteksi terbaru."""
    return vehicle_service.get_vehicles_realtime(db)
