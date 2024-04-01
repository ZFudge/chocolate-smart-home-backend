from paho.mqtt.client import Client, MQTTMessage

import chocolate_smart_home.crud as crud


def device_data_received(client: Client,
                         userdata: None,
                         message: MQTTMessage) -> None:
    payload = message.payload.decode()
    print(payload)
    if payload is None:
        return
    payload_seq = payload.split(",")
    (mqtt_id, device_type_name, remote_name) = payload_seq[:3]
    name = remote_name.split(" - ")[0]

    device_type = crud.get_device_type_by_name(device_type_name)

    if device_type is None:
        device_type = crud.create_device_type(device_type_name)

    device = crud.get_device_by_mqtt_id(mqtt_id)

    if device is None:
        return crud.create_device(mqtt_id,
                                  device_type_name=device_type.name,
                                  remote_name=remote_name,
                                  name=name)

    return crud.update_device(
        mqtt_id,
        device_type_name=device_type.name,
        remote_name=remote_name,
        name=name,
        online= True,
    )
