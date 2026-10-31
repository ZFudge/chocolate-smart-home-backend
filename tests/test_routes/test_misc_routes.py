import datetime as dt
from unittest.mock import patch

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_route_head_broadcast_request_devices_state_calls_request_all_devices_data(
    empty_test_db,
):
    with patch(
        "src.routers.misc.request_all_devices_data",
    ) as request_all_devices_data:
        resp = client.head("/broadcast_request_devices_state/")
        assert resp.status_code == 204
        request_all_devices_data.assert_called_once()


def test_route_head_broadcast_request_devices_state_returns_500_when_raises_exception(
    empty_test_db,
):
    with patch(
        "src.routers.misc.request_all_devices_data",
        side_effect=Exception("Test exception"),
    ):
        resp = client.head("/broadcast_request_devices_state/")
        assert resp.status_code == 500


def test_route_get_health_check_is_healthy(mqtt_client, empty_test_db):
    resp = client.get("/healthcheck")
    assert resp.status_code == 200


def test_route_get_health_check_fails_when_mqtt_client_not_connected(mqtt_client):
    with patch("src.routers.misc.mqtt_client_session") as mqtt_client_session:
        mqtt_client_session.get().is_connected.return_value = False
        assert client.get("/healthcheck").status_code == 500


def test_route_get_health_check_fails_without_db_connection(mqtt_client, empty_test_db):
    with patch("src.routers.misc.db_session") as db_session:
        db_session.get().is_active = False
        assert client.get("/healthcheck").status_code == 500


def test_route__request_all_device_data_last_sent__returns_last_sent_datetime(
    mqtt_client, empty_test_db
):
    with patch(
        "src.routers.misc.get_request_all_device_data_last_sent_as_dt"
    ) as get_request_all_device_data_last_sent_as_dt:
        get_request_all_device_data_last_sent_as_dt.return_value = dt.datetime(
            2026, 1, 1, 12, 0, 0
        )
        resp = client.get("/request_all_device_data_last_sent/")
        assert resp.status_code == 200
        assert resp.json() == "2026-01-01T12:00:00+00:00"


def test_route__request_all_device_data_last_sent__returns_None(
    mqtt_client, empty_test_db
):
    with patch(
        "src.routers.misc.get_request_all_device_data_last_sent_as_dt"
    ) as get_request_all_device_data_last_sent_as_dt:
        get_request_all_device_data_last_sent_as_dt.return_value = None
        resp = client.get("/request_all_device_data_last_sent/")
        assert resp.status_code == 200
        assert resp.json() is None
