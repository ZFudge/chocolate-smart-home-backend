from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app


client = TestClient(app)


def test_route_broadcast_request_devices_state_calls_request_all_devices_data(
    empty_test_db,
):
    with patch(
        "src.routers.misc.request_all_devices_data",
    ) as request_all_devices_data:
        resp = client.head("/broadcast_request_devices_state/")
        assert resp.status_code == 204
        request_all_devices_data.assert_called_once()


def test_route_broadcast_request_devices_state_returns_500_when_raises_exception(
    empty_test_db,
):
    with patch(
        "src.routers.misc.request_all_devices_data",
        side_effect=Exception("Test exception"),
    ):
        resp = client.head("/broadcast_request_devices_state/")
        assert resp.status_code == 500


def test_route_health_check_is_healthy(mqtt_client, empty_test_db):
    resp = client.get("/healthcheck")
    assert resp.status_code == 200


def test_route_health_check_fails_when_mqtt_client_not_connected(mqtt_client):
    with patch("src.routers.misc.mqtt_client_session") as mqtt_client_session:
        mqtt_client_session.get().is_connected.return_value = False
        assert client.get("/healthcheck").status_code == 500


def test_route_health_check_fails_without_db_connection(mqtt_client, empty_test_db):
    with patch("src.routers.misc.db_session") as db_session:
        db_session.get().is_active = False
        assert client.get("/healthcheck").status_code == 500
