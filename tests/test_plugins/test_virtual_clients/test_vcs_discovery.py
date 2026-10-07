from unittest.mock import call, patch

from src.plugins.virtual_clients import VirtualClientsManager
from src.plugins.virtual_clients.defaults import default_compose_outgoing_msg


def test_discover_extracts_and_registers_virtual_clients_from_seeds(
    vcs_module, mqtt_client
):
    with (
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.utils.iter_nametag",
            return_value=[[None, "test_plugin_name", None]],
        ) as iter_nametag,
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.helper_funcs.import_vcs_module",
            return_value=vcs_module,
        ) as import_vcs_module,
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.subscribe"
        ) as subscribe,
    ):
        VirtualClientsManager().discover()
        iter_nametag.assert_called_once()
        import_vcs_module.assert_called_once_with(
            "test_plugin_name.virtual_client_seeds"
        )
        assert VirtualClientsManager.virtual_clients == {
            900: {
                "name": "Test Virtual Client 0",
                "mqtt_id": 900,
                "device_type_name": "test_plugin_name",
            },
            901: {
                "name": "Test Virtual Client 1",
                "mqtt_id": 901,
                "device_type_name": "test_plugin_name",
            },
            902: {
                "name": "Test Virtual Client 2",
                "mqtt_id": 902,
                "device_type_name": "test_plugin_name",
            },
        }
        data_received_handler = subscribe.call_args_list[1].kwargs["handler"]
        subscribe.assert_has_calls(
            [
                call(topic="/test_plugin_name/900/", handler=data_received_handler),
                call(topic="/test_plugin_name/901/", handler=data_received_handler),
                call(topic="/test_plugin_name/902/", handler=data_received_handler),
            ]
        )


def test_expected_calls_when_plugin_vcs_import_fails(mqtt_client):
    with (
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.utils.iter_nametag",
            return_value=[[None, "test_plugin_name", None]],
        ),
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.helper_funcs.validate_virtual_client_module",
            return_value=False,
        ) as validate_virtual_client_module,
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.helper_funcs.import_vcs_module",
            return_value="test_vcs_module",
        ) as import_vcs_module,
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.VirtualClientsManager.register_virtual_clients_by_plugin"
        ) as register_virtual_clients_by_plugin,
    ):
        VirtualClientsManager().discover()
        import_vcs_module.assert_called_once_with(
            "test_plugin_name.virtual_client_seeds"
        )
        validate_virtual_client_module.assert_called_once_with("test_vcs_module")
        register_virtual_clients_by_plugin.assert_not_called()


def test_subscribe_vc_manager_called_if_virtual_clients_truthy(mqtt_client):
    with (
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.VirtualClientsManager.subscribe_vc_manager"
        ) as subscribe_vc_manager,
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.VirtualClientsManager.discover_virtual_clients",
            side_effect=setattr(
                VirtualClientsManager, "virtual_clients", dict(vcs1=True)
            ),
        ) as discover_virtual_clients,
    ):
        VirtualClientsManager().discover()
        discover_virtual_clients.assert_called_once()
        subscribe_vc_manager.assert_called_once()


def test_convergent_composer_func(vcs_module, mqtt_client, mqtt_message):
    """Test that the compose_func function returns a comma-separated join of the
    defaults.compose_outgoing_msg and the vcs_module.compose_outgoing_msg functions.
    The defaults.compose_outgoing_msg function handles the vc configuration (mqtt id, device type name, remote name).
    The vcs_module.compose_outgoing_msg function handles the device-specific state.
    """
    with patch(
        "src.plugins.virtual_clients.VirtualClientsManager.publish",
        return_value=None,
    ) as publish:

        def composer(vc_state: dict) -> str:
            return f'a={vc_state["a"]}'

        vcs_module.compose_outgoing_msg = composer

        vcs_manager = VirtualClientsManager()
        vcs_manager.register_virtual_clients_by_plugin(vcs_module, "test_vcs_module")

        data_received_handler = VirtualClientsManager.get_data_received_handler(
            vcs_module.parse_incoming_payload
        )
        mqtt_message.topic = b"/900/test_vcs_module/"
        mqtt_message.payload = b"a=5"

        data_received_handler(None, None, mqtt_message)
        publish.assert_called_once_with(
            topic="/receive_device_state/",
            message="900,test_vcs_module,Test Virtual Client 0,a=5",
        )


def test_register_virtual_clients_by_plugin(vcs_module, mqtt_client):
    with (
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.VirtualClientsManager.get_data_received_handler",
        ) as get_data_received_handler,
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.subscribe"
        ) as subscribe,
    ):
        handler = lambda _: None  # noqa E731
        get_data_received_handler.return_value = handler
        VirtualClientsManager().register_virtual_clients_by_plugin(
            vcs_module, "test_vcs_module"
        )
        assert "test_vcs_module" in VirtualClientsManager.outgoing_msg_composer_funcs
        assert VirtualClientsManager.mqtt_id == 903
        assert 3 == len(VirtualClientsManager.virtual_clients)
        subscribe.assert_has_calls(
            [
                call(topic="/test_vcs_module/900/", handler=handler),
                call(topic="/test_vcs_module/901/", handler=handler),
                call(topic="/test_vcs_module/902/", handler=handler),
            ]
        )


def test_default_parse_incoming_payload_func_and_composer_func(
    vcs_module, mqtt_client, mqtt_message
):
    """Test that the default parse_incoming_payload function and composer function are used when the vcs_module does not have a compose_outgoing_msg or parse_incoming_payload function."""
    with (
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.VirtualClientsManager.subscribe_vc"
        ) as subscribe_vc,
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.publish",
            return_value=None,
        ) as publish,
    ):
        delattr(vcs_module, "compose_outgoing_msg")
        delattr(vcs_module, "parse_incoming_payload")

        VirtualClientsManager().register_virtual_clients_by_plugin(
            vcs_module, "test_vcs_module"
        )

        data_received_handler = subscribe_vc.call_args.args[1]

        mqtt_message.topic = b"/900/test_vcs_module/"
        mqtt_message.payload = b"something"

        data_received_handler(None, None, mqtt_message)

        assert VirtualClientsManager.virtual_clients[900]["last_payload"] == "something"
        publish.assert_called_once_with(
            topic="/receive_device_state/",
            message="900,test_vcs_module,Test Virtual Client 0",
        )


def test_get_data_received_handler(vcs_module, mqtt_client, mqtt_message):
    with patch(
        "src.plugins.virtual_clients.VirtualClientsManager.publish",
        return_value=None,
    ) as publish:
        VirtualClientsManager.virtual_clients[123] = {
            "device_type_name": "cabbage_device_type",
            "mqtt_id": 123,
            "name": "cabbage device one",
            "cabbage": "",
        }
        VirtualClientsManager.outgoing_msg_composer_funcs["cabbage_device_type"] = (
            default_compose_outgoing_msg
        )
        data_received_handler = VirtualClientsManager.get_data_received_handler(
            lambda msg: msg.split("=")
        )
        mqtt_message.topic = b"/123/cabbage_device_type/"
        mqtt_message.payload = b"cabbage=99"

        data_received_handler(None, None, mqtt_message)

        assert VirtualClientsManager.virtual_clients[123]["cabbage"] == "99"
        publish.assert_called_once_with(
            topic="/receive_device_state/",
            message="123,cabbage_device_type,cabbage device one",
        )


def test_get_data_received_handler_invalid_mqtt_id(mqtt_message):
    with patch(
        "src.plugins.virtual_clients.VirtualClientsManager.logger.error"
    ) as mock_logger:
        data_received_handler = VirtualClientsManager.get_data_received_handler(
            lambda msg: msg.split("=")
        )
        mqtt_message.topic = b"/c/"
        data_received_handler(None, None, mqtt_message)
        mock_logger.assert_called_once_with(
            "Invalid mqtt_id: : invalid literal for int() with base 10: ''"
        )


def test_publish_all_vc_states(vcs_module, mqtt_client, mqtt_message):
    """Test that the default parse_incoming_payload function and composer function are used when the vcs_module does not have a compose_outgoing_msg or parse_incoming_payload function."""
    with (
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.subscribe"
        ) as subscribe,
        patch(
            "src.plugins.virtual_clients.VirtualClientsManager.publish",
            return_value=None,
        ) as publish,
    ):
        delattr(vcs_module, "compose_outgoing_msg")
        delattr(vcs_module, "parse_incoming_payload")

        VirtualClientsManager().register_virtual_clients_by_plugin(
            vcs_module, "test_vcs_module"
        )
        VirtualClientsManager.subscribe_vc_manager()

        publish_all_vc_states = subscribe.call_args_list[-1].kwargs["handler"]
        publish_all_vc_states(None, None, None)

        publish.assert_has_calls(
            [
                call(
                    topic="/receive_device_state/",
                    message="900,test_vcs_module,Test Virtual Client 0",
                ),
                call(
                    topic="/receive_device_state/",
                    message="901,test_vcs_module,Test Virtual Client 1",
                ),
                call(
                    topic="/receive_device_state/",
                    message="902,test_vcs_module,Test Virtual Client 2",
                ),
            ]
        )
