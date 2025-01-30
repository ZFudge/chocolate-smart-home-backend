from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_create_device_type(empty_test_db):
    resp = client.post(
        "/create_device_type/",
        json={"name": "test_device_type_name"},
    )
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "test_device_type_name",
    }
    assert resp.json() == expected_data


def test_create_duplicate_device_type_fails(empty_test_db):
    device_type_name = "test_device_type_name"
    resp = client.post("/create_device_type/", json={"name": device_type_name})
    resp = client.post("/create_device_type/", json={"name": device_type_name})
    assert resp.status_code == 500
    assert resp.json() == {
        "detail": "Key (name)=(test_device_type_name) already exists."
    }


def test_create_device_type_methods_not_allowed(empty_test_db):
    url = "/create_device_type/"
    assert 405 == client.get(url).status_code
    assert 405 == client.delete(url).status_code
    assert 405 == client.patch(url, json={}).status_code
