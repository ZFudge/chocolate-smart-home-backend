from unittest.mock import call, patch

from src.plugins.virtual_clients.defaults import default_compose_state_as_msg
from src.plugins.virtual_clients.discover_virtual_clients import DiscoverVirtualClients


def test_expected_calls_when_plugin_vcs_import_fails(mqtt_client):
    with (
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.utils.iter_nametag",
            return_value=[[None, "test_plugin_name", None]],
        ),
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.helper_funcs.validate_virtual_client_module",
            return_value=False,
        ) as validate_virtual_client_module,
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.helper_funcs.import_vcs_module",
            return_value="test_vcs_module",
        ) as import_vcs_module,
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.DiscoverVirtualClients.register_virtual_clients_by_plugin"
        ) as register_virtual_clients_by_plugin,
    ):
        DiscoverVirtualClients()
        import_vcs_module.assert_called_once_with(
            "test_plugin_name.virtual_client_seeds"
        )
        validate_virtual_client_module.assert_called_once_with("test_vcs_module")
        register_virtual_clients_by_plugin.assert_not_called()


def test_subscribe_clients_called_if_virtual_clients_truthy(mqtt_client):
    with (
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.DiscoverVirtualClients.subscribe_clients"
        ) as subscribe_clients,
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.DiscoverVirtualClients.discover_virtual_clients",
            side_effect=setattr(
                DiscoverVirtualClients, "virtual_clients", dict(vcs1=True)
            ),
        ) as discover_virtual_clients,
    ):
        DiscoverVirtualClients()
        discover_virtual_clients.assert_called_once()
        subscribe_clients.assert_called_once()


def test_register_virtual_clients_by_plugin(vcs_module, mqtt_client):
    with (
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.DiscoverVirtualClients.__init__",
            return_value=None,
        ),
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.DiscoverVirtualClients.get_data_received_handler",
        ) as get_data_received_handler,
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.subscribe"
        ) as subscribe,
    ):
        handler = lambda _: None  # noqa E731
        get_data_received_handler.return_value = handler
        DiscoverVirtualClients().register_virtual_clients_by_plugin(
            vcs_module, "test_module"
        )
        assert "test_module" in DiscoverVirtualClients.compose_funcs_mapping
        assert DiscoverVirtualClients.mqtt_id == 903
        assert 3 == len(DiscoverVirtualClients.virtual_clients)
        subscribe.assert_has_calls(
            [
                call(topic="/test_module/900/", handler=handler),
                call(topic="/test_module/901/", handler=handler),
                call(topic="/test_module/902/", handler=handler),
            ]
        )


def test_get_data_received_handler(vcs_module, mqtt_client, mqtt_message):
    with (
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.DiscoverVirtualClients.__init__",
            return_value=None,
        ),
        patch(
            "src.plugins.virtual_clients.discover_virtual_clients.publish",
            return_value=None,
        ) as publish,
    ):
        DiscoverVirtualClients.virtual_clients[123] = {
            "device_type_name": "cabbage_device_type",
            "mqtt_id": 123,
            "name": "cabbage device one",
            "cabbage": '',
        }
        DiscoverVirtualClients.compose_funcs_mapping["cabbage_device_type"] = (
            default_compose_state_as_msg
        )
        data_received_handler = DiscoverVirtualClients.get_data_received_handler(
            lambda msg: msg.split("=")
        )
        mqtt_message.topic = b"/123/cabbage_device_type/"
        mqtt_message.payload = b"cabbage=99"

        data_received_handler(None, None, mqtt_message)

        assert DiscoverVirtualClients.virtual_clients[123]["cabbage"] == "99"
        publish.assert_called_once_with(
            topic="/receive_device_state/",
            message="123,cabbage_device_type,cabbage device one",
        )
