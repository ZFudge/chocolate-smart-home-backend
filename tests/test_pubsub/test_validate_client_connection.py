from unittest.mock import Mock

from src.pubsub.validate_client_connection import validate_client_connection


def test_pubsub_validate_client_connection_when_client_is_not_connected(mqtt_client):
    mqtt_client.is_connected.return_value = False
    f = Mock()
    wrapper = validate_client_connection(f)
    assert wrapper() is None
    f.assert_not_called()


def test_pubsub_validate_client_connection_when_client_is_connected(mqtt_client):
    mqtt_client.is_connected.return_value = True
    f = Mock()
    wrapper = validate_client_connection(f)
    assert callable(wrapper)
    wrapper()
    f.assert_called()
