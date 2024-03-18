from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from chocolate_smart_home import crud, schemas
from chocolate_smart_home.database import Base
from chocolate_smart_home.dependencies import get_db
from chocolate_smart_home.main import app


DB_URL = "postgresql://"
PG_USER = "testuser"
PG_PW = "testpassword"
PG_HOST = "127.0.0.1"
PG_PORT = 15432
PG_DATABASE = "testdb"

SQLALCHEMY_DATABASE_URL = f"{DB_URL}{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

def test_create_device():
    db = next(override_get_db())
    device_data = dict(mqtt_id=123, remote_name="example_test_name",
                       name="test_name")
    device_data = schemas.DeviceCreate(**device_data)
    device = crud.create_device(db, device_data)

    assert device.mqtt_id == 123
    assert device.remote_name == "example_test_name"
    assert device.name == "test_name"
    assert device.online == False


def test_get_devices():
    response = client.get("/get_devices_data/")
    assert response.status_code == 200, response.text
    data = response.json()

