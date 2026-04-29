from . import Model, Schema


class DeviceManager:
    SERVER_SIDE_COLUMNS = ["scheduled_palette_rotation"]

    def update_server_side_value(self, data: dict) -> Model.PluginModel:
        super().update_server_side_value(data)
        db_plugin_device: Model.PluginModel = (
            self.get_plugin_db_obj_using_device_type_and_mqtt_id(
                device_type_name=data["device_type_name"],
                mqtt_id=data["mqtt_id"],
            )
        )
        setattr(db_plugin_device, data["name"], data["value"])
        super().commit_db_object(db_plugin_device)
        neo_pixel_schema = Schema.NeoPixel(
            on=db_plugin_device.on,
            twinkle=db_plugin_device.twinkle,
            transform=db_plugin_device.transform,
            ms=db_plugin_device.ms,
            brightness=db_plugin_device.brightness,
            palette=db_plugin_device.palette,
            all_twinkle_colors_are_current=db_plugin_device.all_twinkle_colors_are_current,
            pir_enabled=db_plugin_device.pir_enabled,
            pir_armed=db_plugin_device.pir_armed,
            scheduled_palette_rotation=db_plugin_device.scheduled_palette_rotation,
            pir_timeout=db_plugin_device.pir_timeout,
        )
        return neo_pixel_schema

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
        plugin_device.transform = neo_pixel_schema.transform
        plugin_device.ms = neo_pixel_schema.ms
        plugin_device.brightness = neo_pixel_schema.brightness
        plugin_device.palette = neo_pixel_schema.palette
        plugin_device.pir_enabled = neo_pixel_schema.pir_enabled
        plugin_device.pir_armed = neo_pixel_schema.pir_armed
        plugin_device.pir_timeout = neo_pixel_schema.pir_timeout
        # Add server side values
        device_schema.plugin.scheduled_palette_rotation = (
            plugin_device.scheduled_palette_rotation
        )
        super().commit_db_object(plugin_device)
        return db_device
