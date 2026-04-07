from src import schemas, models


def device_mod_obj_to_frontend_schema(
    device: models.Device | None,
) -> schemas.DeviceFrontend | None:
    if device is None:
        return None
    return schemas.DeviceFrontend(
        mqtt_id=device.mqtt_id,
        remote_name=device.remote_name,
        name=device.name,
        device_type_name=device.device_type.name,
        tags=[tag.id for tag in device.tags] if device.tags else None,
        reboots=device.reboots,
        last_seen=str(device.last_seen) if device.last_seen else None,
        last_update_sent=(
            str(device.last_update_sent) if device.last_update_sent else None
        ),
    )
