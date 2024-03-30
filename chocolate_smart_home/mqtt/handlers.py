from paho.mqtt.client import Client, MQTTMessage
from sqlalchemy.orm import Session

from chocolate_smart_home import dependencies, models
import chocolate_smart_home.schemas as schemas


def device_data_received(client: Client,
                         userdata: None,
                         message: MQTTMessage) -> None:
    payload = message.payload.decode()
    print(payload)
    if payload is None:
        return
    payload_sequence = payload.split(",")
    print(payload_sequence)
    (mqtt_id, device_type_name, remote_name) = payload_sequence[:3]
    name = remote_name.split(" - ")[0]

    db = dependencies.db_session.get()

    db_device = db.query(models.Device).filter(
        models.Device.mqtt_id == mqtt_id
    ).first()
    if db_device is None:
        db_device_data = schemas.DeviceReceived(*(payload_sequence[:3]))
        db_device_type = db.query(models.DeviceType).filter(
            models.DeviceType.name == device_type_name
        ).first()
        if db_device_type is None:
            db_device_type = models.DeviceType(name=device_type_name)
            db.add(db_device_type)
            db.commit()
            db.refresh(db_device_type)

        db_device = models.Device(
            mqtt_id=mqtt_id,
            remote_name=remote_name,
            name=name,
            device_type=db_device_type,
            online=True
        )
        db.add(db_device)
        db.commit()
        db.refresh(db_device)
        print(db_device)
        return

    db_device.remote_name = remote_name
    db_device.name = name
    db_device.online = True
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    print(db_device)
