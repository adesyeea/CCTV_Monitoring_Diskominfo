"""
Pydantic schemas for vehicle / object_real_times responses.
"""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ---------- Base ----------

class VehicleBase(BaseModel):
    """Fields common to all vehicle records."""
    object: str
    count: int
    direction: int
    device_id: Optional[str] = None


# ---------- Read (response) ----------

class VehicleRead(VehicleBase):
    """Full vehicle record returned by the API."""
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class VehicleSimple(BaseModel):
    """Simplified record — used for /vehicles endpoint (no id)."""
    object: str
    count: int
    direction: int
    device_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---------- Aggregation responses ----------

class VehicleSummary(BaseModel):
    """object + total count — used for masuk/keluar/today endpoints."""
    object: str
    total: int


class VehiclePerCCTV(BaseModel):
    """Per-device aggregation."""
    device_id: Optional[str] = None
    object: str
    total: int


class VehicleHourly(BaseModel):
    """Per-hour aggregation."""
    jam: int
    total: int


class VehicleRealtime(BaseModel):
    """Realtime record (latest detections)."""
    object: str
    direction: int
    device_id: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
