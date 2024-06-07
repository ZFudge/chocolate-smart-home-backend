from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_update_device_name_is_server_side_name_true(populated_test_db):
    resp = client.put(
        "/update_device_name/1",
        json={"id": 1, "name": "New Name"},
    )
    assert resp.status_code == 200
    expected_data = {
        "id": 1,
        "name": "New Name",
        "is_server_side_name": True,
    }
    assert resp.json() == expected_data


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


def test_update_device_name_idempotent(populated_test_db):
    resp_1 = client.put(
        "/update_device_name/1",
        json={"id": 1, "name": "New Name"},
    )
    resp_2 = client.put(
        "/update_device_name/1",
        json={"id": 1, "name": "New Name"},
    )
    assert resp_1.status_code == 200
    assert resp_2.status_code == 200

    data_1 = resp_1.json()
    data_2 = resp_2.json()
    assert data_1["name"] == "New Name"
    assert data_1["name"] == data_2["name"]
