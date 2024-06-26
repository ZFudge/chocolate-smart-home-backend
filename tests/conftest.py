from contextvars import ContextVar

import pytest
from sqlalchemy.orm import Session, sessionmaker

from chocolate_smart_home import models
from chocolate_smart_home.database import Base
from chocolate_smart_home.dependencies import db_session, engine, get_db
from chocolate_smart_home.main import app


def db_closure():

    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    Base.metadata.create_all(bind=engine)

    db: Session | None = None

    def db_func():
        nonlocal db
        if db is None:
            db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    return db_func


@pytest.fixture
def empty_test_db():
    override_get_db = db_closure()
    app.dependency_overrides[get_db] = override_get_db

    override_db_session: ContextVar[Session] = ContextVar(
        "db_session", default=next(override_get_db())
    )
    db_session.set(next(override_get_db()))
    app.dependency_overrides[db_session] = override_db_session

    yield db_session.get()

    db_session.get().query(models.Device).delete()
    db_session.get().query(models.DeviceName).delete()
    db_session.get().query(models.Client).delete()
    db_session.get().query(models.DeviceType).delete()
    db_session.get().query(models.Space).delete()
    db_session.get().commit()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def populated_test_db(empty_test_db):
    test_db = empty_test_db

    client_1 = models.Client(mqtt_id=123)
    client_2 = models.Client(mqtt_id=456)

    name_1 = models.DeviceName(name="Test Device Name 1")
    name_2 = models.DeviceName(name="Test Device Name 2", is_server_side_name=True)

    type_1 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_1")
    type_2 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_2")

    space_1 = models.Space(name="Main Space")
    space_2 = models.Space(name="Other Space")

    device_1 = models.Device(
        online=True,
        remote_name="Remote Name 1 - 1",
        client=client_1,
        device_type=type_1,
        device_name=name_1,
        space=space_1,
    )
    device_2 = models.Device(
        online=False,
        remote_name="Remote Name 2 - 2",
        client=client_2,
        device_type=type_2,
        device_name=name_2,
    )

    test_db.add(client_1)
    test_db.add(client_2)
    test_db.add(name_1)
    test_db.add(name_2)
    test_db.add(type_1)
    test_db.add(type_2)
    test_db.add(space_1)
    test_db.add(space_2)
    test_db.add(device_1)
    test_db.add(device_2)

    test_db.commit()

    yield test_db
