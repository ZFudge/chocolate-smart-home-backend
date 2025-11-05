from unittest.mock import call, patch

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_update_leonardo_device(populated_test_db):
    with patch(
        "src.plugins.device_plugins.leonardo.router.publish_message"
    ) as publish_message:
        resp = client.post("/leonardo/1/wake")
        publish_message.assert_called_once_with(leonardo_device_id=1, msg="wake")

    assert resp.status_code == 204


def test_update_leonardo_device_invalid_message(populated_test_db):
    resp = client.post("/leonardo/1/invalid")
    assert resp.status_code == 400
    assert resp.json() == {"detail": "Invalid message: invalid"}
