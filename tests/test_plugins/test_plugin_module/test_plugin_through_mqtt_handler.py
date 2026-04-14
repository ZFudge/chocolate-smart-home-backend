from src.crud import get_plugin_db_obj_using_device_type_and_mqtt_id
from src.plugins import PluginsManager
from src.pubsub.handler import mqtt_message_handler


def test_mqtt_handler_parses_controller_message_and_loads_controller_data_into_device_schema(
    empty_test_db, example_plugin_path, mqtt_message
):
    PluginsManager.load_plugin_from_path(example_plugin_path)
    mqtt_message.payload = b"123,example_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)
    plugin_db_obj = get_plugin_db_obj_using_device_type_and_mqtt_id(
        "example_plugin", 123
    )
    assert plugin_db_obj.count == 7


def test_mqtt_handler_parses_controller_message_and_creates_db_device(
    empty_test_db, example_plugin_path, mqtt_message
):
    PluginsManager.load_plugin_from_path(example_plugin_path)
    mqtt_message.payload = b"123,example_plugin,test_remote_name,7"
    mqtt_message_handler(None, None, mqtt_message)
    plugin_db_obj = get_plugin_db_obj_using_device_type_and_mqtt_id(
        "example_plugin", 123
    )
    assert plugin_db_obj.count == 7
