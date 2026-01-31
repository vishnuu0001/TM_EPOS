import os
import sys
import uuid
import importlib.util
from pathlib import Path
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient


BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

test_db_path = BASE_DIR / "data" / f"epos_test_{uuid.uuid4().hex}.db"
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"
os.environ.setdefault("SEED_DATA_ON_STARTUP", "false")
os.environ.setdefault("SEED_ON_FIRST_BOOT", "false")


class DummyUser(dict):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__dict__.update(kwargs)


def _fake_user():
    return DummyUser(id=str(uuid.uuid4()), email="tester@example.com", roles=["admin"])


def _load_app(service_name: str):
    for module_name in list(sys.modules):
        if module_name == "shared" or module_name.startswith("shared."):
            del sys.modules[module_name]

    if str(BASE_DIR) in sys.path:
        sys.path.remove(str(BASE_DIR))
    sys.path.insert(0, str(BASE_DIR))
    service_dir = BASE_DIR / "services" / service_name
    if not service_dir.exists():
        raise RuntimeError(f"Service directory not found: {service_dir}")

    sys.path.insert(1, str(service_dir))
    for module_name in ["models", "schemas"]:
        if module_name in sys.modules:
            del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(
        f"{service_name}_main", service_dir / "main.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    sys.path.pop(1)
    return module.app


def _make_client(app):
    from shared.auth import get_current_user

    async def _override_user():
        return _fake_user()

    app.dependency_overrides[get_current_user] = _override_user
    return TestClient(app)


def _assert_status(response, expected=200, label=""):
    if response.status_code != expected:
        raise AssertionError(
            f"{label} expected {expected}, got {response.status_code}: {response.text}"
        )


def _iso(dt: datetime) -> str:
    return dt.replace(microsecond=0).isoformat()


def test_canteen():
    app = _load_app("canteen")
    with _make_client(app) as client:
        employee_id = f"EMP-{uuid.uuid4().hex[:8]}"
        worker_payload = {
            "full_name": "Test Worker",
            "employee_id": employee_id,
            "worker_type": "permanent",
            "phone": "9999999999",
        }
        response = client.post("/workers", json=worker_payload)
        _assert_status(response, label="canteen create worker")
        worker_id = response.json()["id"]

        response = client.get("/workers")
        _assert_status(response, label="canteen list workers")

        response = client.get(f"/workers/{worker_id}")
        _assert_status(response, label="canteen get worker")

        response = client.put(f"/workers/{worker_id}", json={"canteen_access": False})
        _assert_status(response, label="canteen update worker")


def test_colony_maintenance():
    app = _load_app("colony-maintenance")
    with _make_client(app) as client:
        payload = {
            "quarter_number": "Q1-01",
            "category": "plumbing",
            "description": "Leaky pipe in bathroom",
            "priority": "medium",
        }
        response = client.post("/requests", json=payload)
        _assert_status(response, label="colony create request")
        request_id = response.json()["id"]

        response = client.get("/requests")
        _assert_status(response, label="colony list requests")

        response = client.get(f"/requests/{request_id}")
        _assert_status(response, label="colony get request")

        response = client.put(
            f"/requests/{request_id}",
            json={"priority": "high", "estimated_cost": 1500.0},
        )
        _assert_status(response, label="colony update request")


def test_equipment():
    app = _load_app("equipment")
    with _make_client(app) as client:
        payload = {
            "equipment_number": f"EQ-{uuid.uuid4().hex[:6]}",
            "name": "Hydraulic Crane",
            "equipment_type": "CRANE",
            "hourly_rate": 250.0,
            "location": "Yard",
        }
        response = client.post("/equipment", json=payload)
        _assert_status(response, label="equipment create")
        equipment_id = response.json()["id"]

        response = client.get("/equipment")
        _assert_status(response, label="equipment list")

        response = client.get(f"/equipment/{equipment_id}")
        _assert_status(response, label="equipment get")

        response = client.put(
            f"/equipment/{equipment_id}",
            json={"location": "Service Bay", "hourly_rate": 275.0},
        )
        _assert_status(response, label="equipment update")


def test_guesthouse():
    app = _load_app("guesthouse")
    with _make_client(app) as client:
        payload = {
            "room_number": f"R-{uuid.uuid4().hex[:4]}",
            "room_type": "single",
            "floor": 1,
            "capacity": 1,
            "rate_per_night": 1200.0,
        }
        response = client.post("/rooms", json=payload)
        _assert_status(response, label="guesthouse create room")
        room_id = response.json()["id"]

        response = client.get("/rooms")
        _assert_status(response, label="guesthouse list rooms")

        response = client.get(f"/rooms/{room_id}")
        _assert_status(response, label="guesthouse get room")

        response = client.put(
            f"/rooms/{room_id}",
            json={"rate_per_night": 1350.0, "capacity": 2},
        )
        _assert_status(response, label="guesthouse update room")


def test_visitor():
    app = _load_app("visitor")
    with _make_client(app) as client:
        visit_date = _iso(datetime.now(timezone.utc) + timedelta(days=1))
        payload = {
            "visitor_name": "Test Visitor",
            "visitor_phone": "8888888888",
            "visitor_type": "guest",
            "sponsor_employee_id": "EMP-1001",
            "sponsor_name": "Host User",
            "purpose_of_visit": "Site tour",
            "visit_date": visit_date,
            "expected_duration": 2,
        }
        response = client.post("/requests", json=payload)
        _assert_status(response, label="visitor create request")
        request_id = response.json()["id"]

        response = client.get("/requests")
        _assert_status(response, label="visitor list requests")

        response = client.get(f"/requests/{request_id}")
        _assert_status(response, label="visitor get request")

        response = client.put(
            f"/requests/{request_id}",
            json={"purpose_of_visit": "Updated purpose"},
        )
        _assert_status(response, label="visitor update request")


def test_vigilance():
    app = _load_app("vigilance")
    with _make_client(app) as client:
        start = datetime.now(timezone.utc) + timedelta(hours=1)
        end = start + timedelta(hours=8)
        payload = {
            "guard_id": str(uuid.uuid4()),
            "guard_name": "Guard Alpha",
            "duty_date": _iso(start),
            "shift_type": "morning",
            "shift_start": _iso(start),
            "shift_end": _iso(end),
            "assigned_gate": "G1",
        }
        response = client.post("/roster", json=payload)
        _assert_status(response, label="vigilance create roster")
        roster_id = response.json()["id"]

        response = client.get("/roster")
        _assert_status(response, label="vigilance list roster")

        response = client.get(f"/roster/{roster_id}")
        _assert_status(response, label="vigilance get roster")

        response = client.put(
            f"/roster/{roster_id}",
            json={"status": "active", "remarks": "On time"},
        )
        _assert_status(response, label="vigilance update roster")


def test_vehicle():
    app = _load_app("vehicle")
    with _make_client(app) as client:
        vehicle_payload = {
            "registration_number": f"REG-{uuid.uuid4().hex[:6]}",
            "vehicle_type": "CAR",
            "make": "TestMake",
            "model": "TestModel",
            "year": 2024,
            "capacity": 4,
        }
        response = client.post("/vehicles", json=vehicle_payload)
        _assert_status(response, label="vehicle create vehicle")
        vehicle_id = response.json()["id"]

        response = client.get("/vehicles")
        _assert_status(response, label="vehicle list vehicles")

        driver_payload = {
            "user_id": f"U-{uuid.uuid4().hex[:6]}",
            "license_number": f"LIC-{uuid.uuid4().hex[:6]}",
            "license_expiry": _iso(datetime.now(timezone.utc) + timedelta(days=365)),
        }
        response = client.post("/drivers", json=driver_payload)
        _assert_status(response, label="vehicle create driver")
        driver_id = response.json()["id"]

        requisition_payload = {
            "purpose": "Client visit",
            "destination": "Main Gate",
            "departure_date": _iso(datetime.now(timezone.utc) + timedelta(hours=2)),
            "number_of_passengers": 2,
        }
        response = client.post("/requisitions", json=requisition_payload)
        _assert_status(response, label="vehicle create requisition")
        requisition_id = response.json()["id"]

        response = client.post(
            f"/requisitions/{requisition_id}/approve",
            params={"vehicle_id": vehicle_id},
        )
        _assert_status(response, label="vehicle approve requisition")

        trip_payload = {"driver_id": driver_id, "requisition_id": requisition_id}
        response = client.post("/trips", json=trip_payload)
        _assert_status(response, label="vehicle create trip")
        trip_id = response.json()["id"]

        response = client.put(
            f"/trips/{trip_id}/start",
            params={"start_odometer": 1000.0},
        )
        _assert_status(response, label="vehicle start trip")

        response = client.put(
            f"/trips/{trip_id}/end",
            params={"end_odometer": 1015.5},
        )
        _assert_status(response, label="vehicle end trip")


def run_all():
    test_canteen()
    test_colony_maintenance()
    test_equipment()
    test_guesthouse()
    test_visitor()
    test_vigilance()
    test_vehicle()
    print("All CRUD checks passed.")


if __name__ == "__main__":
    run_all()
