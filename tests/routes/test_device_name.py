from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_update_device_name_is_server_side_name_true(populated_test_db):
    resp = client.put(
        "/update_device_name/1",
        json={"id": 1, "name": "New Name"},
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["name"] == "New Name"
    assert data["is_server_side_name"] is True


def test_update_device_name_is_server_side_name_false(populated_test_db):
    resp = client.put(
        "/update_device_name/1",
        json={"id": 1, "name": "Remote Name 1"},
    )

    assert resp.status_code == 200

    data = resp.json()
    assert data["name"] == "Remote Name 1"
    assert data["is_server_side_name"] is False
    

def test_update_device_name_no_result_fails(empty_test_db):
    resp = client.put(
        "/update_device_name/1",
        json={"id": 1, "name": "Remote Name 1"},
    )

    assert resp.status_code == 500
