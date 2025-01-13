import pytest
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from chocolate_smart_home import dependencies, models


def test_used_client_raises_device_client_error(empty_test_db):
    client = models.Client(mqtt_id=555)
    name = models.DeviceName(name="Test Device")
    other_name = models.DeviceName(name="Another Test Device")
    device_type = models.DeviceType(name="test_device_type")

    device = models.Device(
        client=client,
        device_name=name,
        device_type=device_type,
        remote_name="Remote Name - 1",
    )

    db: Session = dependencies.db_session.get()
    db.add(device)
    db.commit()

    expected_text = (
        "([DeviceClientError("
        "Client object with mqtt_id of 555 is already assigned to Device "
        "object of Device.id 1"
        ")])"
    )

    with pytest.raises(SQLAlchemyError, match=expected_text):
        models.Device(client=client, device_name=other_name)


def test_used_name_raises_device_name_error(empty_test_db):
    client = models.Client(mqtt_id=555)
    other_client = models.Client(mqtt_id=777)
    name = models.DeviceName(name="Test Device")
    device_type = models.DeviceType(name="test_device_type")

    device = models.Device(
        client=client,
        device_name=name,
        device_type=device_type,
        remote_name="Remote Name - 1",
    )

    db: Session = dependencies.db_session.get()
    db.add(device)
    db.commit()

    expected_text = (
        "([DeviceNameError("
        "DeviceName object with DeviceName.name of Test Device is already "
        "assigned to Device object of Device.id 1"
        ")])"
    )

    with pytest.raises(SQLAlchemyError, match=expected_text):
        models.Device(device_name=name, client=other_client)


def test_used_client_and_name_raises_device_client_and_device_name_errors(
    empty_test_db,
):
    client = models.Client(mqtt_id=555)
    name = models.DeviceName(name="Test Device")
    device_type = models.DeviceType(name="test_device_type")

    device = models.Device(
        client=client,
        device_name=name,
        device_type=device_type,
        remote_name="Remote Name - 1",
    )

    db: Session = dependencies.db_session.get()
    db.add(device)
    db.commit()

    expected_text = (
        "([DeviceClientError("
        "Client object with mqtt_id of 555 is already assigned to Device "
        "object of Device.id 1),"
        "DeviceNameError("
        "DeviceName object with DeviceName.name of Test Device is already "
        "assigned to Device object of Device.id 1"
        ")])"
    )

    with pytest.raises(SQLAlchemyError, match=expected_text):
        models.Device(client=client, device_name=name)
