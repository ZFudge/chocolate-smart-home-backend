import logging

from . import Model, Schema


logger = logging.getLogger()


class DeviceManager:
    def create_device(self, device_schema):
        db_device = super().create_device(device_schema)
        example_plugin_schema: Schema.ExamplePluginSchema = device_schema.plugin
        plugin_device = Model.PluginModel(
            mqtt_id=device_schema.mqtt_id, count=example_plugin_schema.count
        )
        super().commit_db_object(plugin_device)
        return db_device

    def update_device(self, device_schema, *_):
        db_device = super().update_device(device_schema)
        plugin_device: (
            Model.PluginModel
        ) = super().get_plugin_db_obj_using_device_type_and_mqtt_id(
            device_type_name=device_schema.device_type_name,
            mqtt_id=device_schema.mqtt_id,
        )
        example_plugin_schema: Schema.ExamplePluginSchema = device_schema.plugin
        plugin_device.count = example_plugin_schema.count
        super().commit_db_object(plugin_device)
        return db_device
