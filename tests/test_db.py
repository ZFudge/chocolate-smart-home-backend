from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from chocolate_smart_home.database import Base
from chocolate_smart_home.dependencies import get_db
from chocolate_smart_home.main import app
from chocolate_smart_home import crud


DB_URL = "postgresql://"
PG_USER = "testuser"
PG_PW = "testpassword"
PG_HOST = "127.0.0.1"
PG_PORT = 15432
PG_DATABASE = "testdb"

SQLALCHEMY_DATABASE_URL = f"{DB_URL}{PG_USER}:{PG_PW}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# def test_create_device():
#     print('test_create_device')
#     db = get_db()
#     device_data = dict(mqtt_id=7, remote_name="test remote name",
#                        name="test name", online=False)
#     device = crud.create_device(db, device_data)
#     print(device)

def test_get_devices():
    print('test_get_devices')
    response = client.get("/get_devices_data/")
    assert response.status_code == 200, response.text
    data = response.json()
    print(data)


# def test_create_user():
#     response = client.post(
#         "/users/",
#         json={"email": "deadpool@example.com", "password": "chimichangas4life"},
#     )
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["email"] == "deadpool@example.com"
#     assert "id" in data
#     user_id = data["id"]

#     response = client.get(f"/users/{user_id}")
#     assert response.status_code == 200, response.text
#     data = response.json()
#     assert data["email"] == "deadpool@example.com"
#     assert data["id"] == user_id

