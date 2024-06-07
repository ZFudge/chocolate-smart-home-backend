from chocolate_smart_home import models, schemas


def client_to_schema(client: models.Client) -> schemas.Client:
    return schemas.Client(id=client.id, mqtt_id=client.mqtt_id)


def device_name_to_schema(device_name: models.DeviceName) -> schemas.DeviceName:
    return schemas.DeviceName(
        id=device_name.id,
        name=device_name.name,
        is_server_side_name=device_name.is_server_side_name,
    )


def device_type_to_schema(device_type_data: models.Device) -> schemas.DeviceType:
    return schemas.DeviceType(id=device_type_data.id, name=device_type_data.name)


def space_to_schema(space: models.Space | None) -> schemas.Space | schemas.SpaceEmpty:
    if space is None:
        return schemas.SpaceEmpty()
    return schemas.Space(id=space.id, name=space.name)


def device_to_schema(device_data: models.Device) -> schemas.Device:
    return schemas.Device(
        id=device_data.id,
        client=client_to_schema(device_data.client),
        device_name=device_name_to_schema(device_data.device_name),
        device_type=device_type_to_schema(device_data.device_type),
        space=space_to_schema(device_data.space),
        remote_name=device_data.remote_name,
        online=device_data.online,
        reboots=device_data.reboots,
    )
