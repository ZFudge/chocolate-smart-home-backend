from paho.mqtt.client import Client, MQTTMessage


def get_device_data_received_handler(
    get_device_type_by_name,
    get_device_by_mqtt_id,
    create_device,
    update_device,
    **kwargs
):
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

        device_type = get_device_type_by_name(device_type_name)

        device = get_device_by_mqtt_id(mqtt_id)

        if device is None:
            return create_device(mqtt_id,
                                 device_type_name=device_type.name,
                                 remote_name=remote_name,
                                 name=name)

        return update_device(
            mqtt_id,
            device_type_name=device_type.name,
            remote_name=remote_name,
            name=name,
            online=True,
        )

    return device_data_received
