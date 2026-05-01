from sqlalchemy import Column, Integer, String, DateTime, func

from app.db.database import Base


class ObjectRealTime(Base):
    """
    ORM model mapping to the `object_real_times` table.

    Columns:
        id         — Primary key
        object     — Vehicle/object type name (e.g. 'car', 'motorcycle')
        count      — Number of objects detected in this record
        direction  — 1 = masuk (in), 2 = keluar (out)
        device_id  — CCTV device identifier
        created_at — Timestamp of the detection
    """

    __tablename__ = "object_real_times"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    object = Column("object", String(100), nullable=False)
    count = Column(Integer, nullable=False, default=0)
    direction = Column(Integer, nullable=False)
    device_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return (
            f"<ObjectRealTime(id={self.id}, object='{self.object}', "
            f"count={self.count}, direction={self.direction})>"
        )
