import os

from src.mqtt import get_configured_mqtt_client


def test_get_configured_mqtt_client_when_client_id_suffix_is_set(mqtt_client):
    mqtt_client.is_connected.return_value = True
    client = get_configured_mqtt_client()
    assert client._client_id == b"pytest-CSM-FASTAPI-SERVER-DEV"


def test_get_configured_mqtt_client_when_client_id_suffix_is_not_set(mqtt_client):
    del os.environ["MQTT_CLIENT_ID_PREFIX"]
    mqtt_client.is_connected.return_value = True
    client = get_configured_mqtt_client()
    assert client._client_id == b"CSM-FASTAPI-SERVER-DEV"
