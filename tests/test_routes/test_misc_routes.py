from unittest.mock import Mock, patch

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_broadcast_request_devices_state_calls_request_all_devices_data(empty_test_db):
    with patch(
        "src.routers.misc.get_mqtt_client",
        side_effect=Mock(request_all_devices_data=Mock()),
    ) as request_all_devices_data:
        resp = client.head("/broadcast_request_devices_state/")
        assert resp.status_code == 204
        request_all_devices_data().request_all_devices_data.assert_called_once()


def test_raises_exception_broadcast_request_devices_state(empty_test_db):
    with patch(
        "src.routers.misc.get_mqtt_client", side_effect=Exception("Test exception")
    ):
        resp = client.head("/broadcast_request_devices_state/")
        assert resp.status_code == 500
