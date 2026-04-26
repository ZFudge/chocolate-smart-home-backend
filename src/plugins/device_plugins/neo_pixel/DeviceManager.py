import logging

from . import Model, Schema


logger = logging.getLogger()


class DeviceManager:
    def create_device(self, device_schema):
        db_device = super().create_device(device_schema)
        neo_pixel_schema: Schema.NeoPixel = device_schema.plugin
        plugin_device = Model.PluginModel(
            mqtt_id=device_schema.mqtt_id,
            on=neo_pixel_schema.on,
            twinkle=neo_pixel_schema.twinkle,
            all_twinkle_colors_are_current=neo_pixel_schema.all_twinkle_colors_are_current,
            scheduled_palette_rotation=neo_pixel_schema.scheduled_palette_rotation,
            transform=neo_pixel_schema.transform,
            ms=neo_pixel_schema.ms,
            brightness=neo_pixel_schema.brightness,
            palette=neo_pixel_schema.palette,
            pir_enabled=neo_pixel_schema.pir_enabled,
            pir_armed=neo_pixel_schema.pir_armed,
            pir_timeout=neo_pixel_schema.pir_timeout,
        )
        super().commit_db_object(plugin_device)
        return db_device

    def update_device(self, device_schema):
        db_device = super().update_device(device_schema)
        neo_pixel_schema: Schema.NeoPixel = device_schema.plugin
        plugin_device: Model.PluginModel = (
            self.get_plugin_db_obj_using_device_type_and_mqtt_id(
                device_type_name=device_schema.device_type_name,
                mqtt_id=device_schema.mqtt_id,
            )
        )
        plugin_device.on = neo_pixel_schema.on
        plugin_device.twinkle = neo_pixel_schema.twinkle
        plugin_device.all_twinkle_colors_are_current = (
            neo_pixel_schema.all_twinkle_colors_are_current
        )
        plugin_device.scheduled_palette_rotation = (
            neo_pixel_schema.scheduled_palette_rotation
        )
        plugin_device.transform = neo_pixel_schema.transform
        plugin_device.ms = neo_pixel_schema.ms
        plugin_device.brightness = neo_pixel_schema.brightness
        plugin_device.palette = neo_pixel_schema.palette
        plugin_device.pir_enabled = neo_pixel_schema.pir_enabled
        plugin_device.pir_armed = neo_pixel_schema.pir_armed
        plugin_device.pir_timeout = neo_pixel_schema.pir_timeout
        super().commit_db_object(plugin_device)
        return db_device
