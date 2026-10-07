import logging

from . import Model, Schema


logger = logging.getLogger()


class DeviceManager:
    def create_device(self, device_schema):
        db_device = super().create_device(device_schema)
        test_stateful_simplex_plugin_schema: Schema.StatefulSimplexPluginSchema = (
            device_schema.plugin
        )
        plugin_device = Model.PluginModel(
            mqtt_id=device_schema.mqtt_id,
            sensor_reading=test_stateful_simplex_plugin_schema.sensor_reading,
        )
        super().commit_db_object(plugin_device)
        return db_device

    def update_device(self, device_schema):
        db_device = super().update_device(device_schema)
        test_stateful_simplex_plugin_schema: Schema.StatefulSimplexPluginSchema = (
            device_schema.plugin
        )
        plugin_device: Model.PluginModel = (
            self.get_plugin_db_obj_using_device_type_and_mqtt_id(
                device_type_name=device_schema.device_type_name,
                mqtt_id=device_schema.mqtt_id,
            )
        )
        plugin_device.sensor_reading = (
            test_stateful_simplex_plugin_schema.sensor_reading
        )
        super().commit_db_object(plugin_device)
        return db_device
