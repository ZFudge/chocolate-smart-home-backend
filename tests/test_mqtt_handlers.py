from unittest.mock import Mock

from paho.mqtt.client import MQTTMessage
import pytest

from chocolate_smart_home.mqtt.handler import MQTTMessageHandler
import chocolate_smart_home.crud as crud


@pytest.fixture
def crud_kwargs():
    yield dict([(k, getattr(crud, k)) for k in dir(crud)])


@pytest.fixture
def handler(crud_kwargs):
    yield MQTTMessageHandler(**crud_kwargs)


def test_device_data_received_results(test_database, handler):
    message = MQTTMessage(b'test_topic')
    message.payload = b"1,DEVICE_TYPE,Remote Name - unique identifier"
    device = handler.device_data_received(0, None, message)

    assert device.mqtt_id == 1
    assert device.device_type.name == "DEVICE_TYPE"
    assert device.remote_name == "Remote Name - unique identifier"
    assert device.name == "Remote Name"


def test_method_calls(test_database, crud_kwargs):
    get_new_or_existing_device_type_by_name = Mock(wraps=crud.get_new_or_existing_device_type_by_name)
    get_device_by_mqtt_id = Mock(wraps=crud.get_device_by_mqtt_id)
    create_device = Mock(wraps=crud.create_device)
    update_device = Mock(wraps=crud.update_device)

    crud_kwargs['get_new_or_existing_device_type_by_name'] = get_new_or_existing_device_type_by_name
    crud_kwargs['get_device_by_mqtt_id'] = get_device_by_mqtt_id
    crud_kwargs['create_device'] = create_device
    crud_kwargs['update_device'] = update_device

    handler = MQTTMessageHandler(**crud_kwargs)

    message = MQTTMessage(b'test_topic')
    message.payload = b"1,DEVICE_TYPE,Remote Name - unique identifier"

    # First handle
    handler.device_data_received(0, None, message)

    get_new_or_existing_device_type_by_name.assert_called_once_with("DEVICE_TYPE")
    get_device_by_mqtt_id.assert_called_once_with("1")
    create_device.assert_called_once_with(
        "1",
        device_type_name="DEVICE_TYPE",
        remote_name="Remote Name - unique identifier",
        name="Remote Name",
    )
    update_device.assert_not_called()

    # Second handle
    handler.device_data_received(0, None, message)

    assert get_new_or_existing_device_type_by_name.call_count == 2
    assert get_device_by_mqtt_id.call_count == 2
    create_device.assert_called_once()
    update_device.assert_called_once_with(
        "1",
        device_type_name="DEVICE_TYPE",
        remote_name="Remote Name - unique identifier",
        name="Remote Name"
    )

    # Third handle
    handler.device_data_received(0, None, message)

    assert get_new_or_existing_device_type_by_name.call_count == 3
    assert get_device_by_mqtt_id.call_count == 3
    create_device.assert_called_once()
    assert update_device.call_count == 2
