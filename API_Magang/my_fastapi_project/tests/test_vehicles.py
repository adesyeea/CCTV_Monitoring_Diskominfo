"""
Tests for vehicle endpoints.
"""

from app.db.models import ObjectRealTime


def _seed_data(db_session):
    """Insert sample data into the test database."""
    records = [
        ObjectRealTime(object="car", count=5, direction=1, device_id="CAM-01"),
        ObjectRealTime(object="motorcycle", count=3, direction=1, device_id="CAM-01"),
        ObjectRealTime(object="car", count=2, direction=2, device_id="CAM-02"),
        ObjectRealTime(object="truck", count=1, direction=2, device_id="CAM-02"),
    ]
    db_session.add_all(records)
    db_session.commit()


def test_get_all_vehicles(client, db_session):
    _seed_data(db_session)
    response = client.get("/vehicles")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4


def test_kendaraan_masuk(client, db_session):
    _seed_data(db_session)
    response = client.get("/vehicles/masuk")
    assert response.status_code == 200
    data = response.json()
    # direction=1 → car(5) + motorcycle(3)
    assert len(data) == 2
    objects = {item["object"] for item in data}
    assert "car" in objects
    assert "motorcycle" in objects


def test_kendaraan_keluar(client, db_session):
    _seed_data(db_session)
    response = client.get("/vehicles/keluar")
    assert response.status_code == 200
    data = response.json()
    # direction=2 → car(2) + truck(1)
    assert len(data) == 2


def test_kendaraan_per_cctv(client, db_session):
    _seed_data(db_session)
    response = client.get("/vehicles/cctv")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2  # at least CAM-01 and CAM-02 groups


def test_realtime(client, db_session):
    _seed_data(db_session)
    response = client.get("/vehicles/realtime")
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 10
