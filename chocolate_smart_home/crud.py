from sqlalchemy.orm import Session

from chocolate_smart_home import models, schemas


def create_device(db: Session, device: schemas.DeviceCreate) -> schemas.Device:
    db_device = models.Device(
        mqtt_id=device.mqtt_id,
        remote_name=device.remote_name,
        name=device.name,
        online=False,
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def get_devices_data(db: Session) -> list[schemas.Device]:
    return db.query(models.Device).all()


def update_devices_data(
    db: Session, devices_data: list[schemas.DeviceUpdate]
) -> list[schemas.Device]:
    devices_data_by_id = dict([(x.id, x) for x in devices_data])
    device_ids = devices_data_by_id.keys()
    devices = db.query(models.Device).filter(models.Device.id.in_(device_ids)).all()
    for device in devices:
        for attr_name, value in devices_data_by_id.get(device.id):
            if value is None:
                continue
            setattr(device, attr_name, value)
        db.add(device)
    db.commit()
    for device in devices:
        db.refresh(device)
    return devices


def get_spaces_data(db: Session) -> list[schemas.Space]:
    return db.query(models.Space).all()
