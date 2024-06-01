from fastapi.testclient import TestClient

from chocolate_smart_home.main import app


client = TestClient(app)


def test_update_device(empty_test_db):
    resp = client.post(
        "/update_device/1",
        json={
            "mqtt_id": 1,
            "device_type_name": "test_device_type_name",
            "remote_name": "Test Device - 123",
            "name": "",
        },
    )

    assert resp.status_code == 204
