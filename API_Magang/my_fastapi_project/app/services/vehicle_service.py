"""
Vehicle service — all ORM queries for object_real_times.

This replaces every raw SQL query from the original api.py with
proper SQLAlchemy ORM operations.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from datetime import date
from typing import List, Dict, Any

from app.db.models import ObjectRealTime


def get_all_vehicles(db: Session, limit: int = 100) -> List[ObjectRealTime]:
    """
    SELECT object, count, direction, device_id, created_at
    FROM object_real_times
    ORDER BY created_at DESC
    LIMIT :limit
    """
    return (
        db.query(ObjectRealTime)
        .order_by(ObjectRealTime.created_at.desc())
        .limit(limit)
        .all()
    )


def get_vehicles_masuk(db: Session) -> List[Dict[str, Any]]:
    """
    SELECT object, SUM(count) as total
    FROM object_real_times
    WHERE direction = 1
    GROUP BY object
    """
    rows = (
        db.query(
            ObjectRealTime.object,
            func.sum(ObjectRealTime.count).label("total"),
        )
        .filter(ObjectRealTime.direction == 1)
        .group_by(ObjectRealTime.object)
        .all()
    )
    return [{"object": row.object, "total": int(row.total)} for row in rows]


def get_vehicles_keluar(db: Session) -> List[Dict[str, Any]]:
    """
    SELECT object, SUM(count) as total
    FROM object_real_times
    WHERE direction = 2
    GROUP BY object
    """
    rows = (
        db.query(
            ObjectRealTime.object,
            func.sum(ObjectRealTime.count).label("total"),
        )
        .filter(ObjectRealTime.direction == 2)
        .group_by(ObjectRealTime.object)
        .all()
    )
    return [{"object": row.object, "total": int(row.total)} for row in rows]


def get_vehicles_today(db: Session) -> List[Dict[str, Any]]:
    """
    SELECT object, SUM(count) as total
    FROM object_real_times
    WHERE DATE(created_at) = CURDATE()
    GROUP BY object
    """
    today = date.today()
    rows = (
        db.query(
            ObjectRealTime.object,
            func.sum(ObjectRealTime.count).label("total"),
        )
        .filter(func.date(ObjectRealTime.created_at) == today)
        .group_by(ObjectRealTime.object)
        .all()
    )
    return [{"object": row.object, "total": int(row.total)} for row in rows]


def get_vehicles_per_cctv(db: Session) -> List[Dict[str, Any]]:
    """
    SELECT device_id, object, SUM(count) as total
    FROM object_real_times
    GROUP BY device_id, object
    """
    rows = (
        db.query(
            ObjectRealTime.device_id,
            ObjectRealTime.object,
            func.sum(ObjectRealTime.count).label("total"),
        )
        .group_by(ObjectRealTime.device_id, ObjectRealTime.object)
        .all()
    )
    return [
        {"device_id": row.device_id, "object": row.object, "total": int(row.total)}
        for row in rows
    ]


def get_vehicles_hourly(db: Session) -> List[Dict[str, Any]]:
    """
    SELECT HOUR(created_at) as jam, SUM(count) as total
    FROM object_real_times
    GROUP BY jam
    ORDER BY jam
    """
    hour_col = extract("hour", ObjectRealTime.created_at).label("jam")
    rows = (
        db.query(
            hour_col,
            func.sum(ObjectRealTime.count).label("total"),
        )
        .group_by(hour_col)
        .order_by(hour_col)
        .all()
    )
    return [{"jam": int(row.jam), "total": int(row.total)} for row in rows]


def get_vehicles_realtime(db: Session, limit: int = 10) -> List[ObjectRealTime]:
    """
    SELECT object, direction, device_id, created_at
    FROM object_real_times
    ORDER BY created_at DESC
    LIMIT :limit
    """
    return (
        db.query(ObjectRealTime)
        .order_by(ObjectRealTime.created_at.desc())
        .limit(limit)
        .all()
    )
