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

    db_session.get().query(models.DeviceTag).delete()
    db_session.get().query(models.Device).delete()
    db_session.get().query(models.DeviceType).delete()
    db_session.get().query(models.Tag).delete()
    db_session.get().commit()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def populated_test_db(empty_test_db):
    test_db = empty_test_db

    type_1 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_1")
    type_2 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_2")

    tag_1 = models.Tag(name="Main Tag")
    tag_2 = models.Tag(name="Other Tag")

    device_1 = models.Device(
        mqtt_id=123,
        remote_name="Remote Name 1 - 1",
        name="Test Device Name 1",
        device_type=type_1,
        tags=[tag_1],
        online=True,
    )
    device_2 = models.Device(
        mqtt_id=456,
        remote_name="Remote Name 2 - 2",
        name="Test Device Name 2",
        device_type=type_2,
        online=False,
    )

    test_db.add(type_1)
    test_db.add(type_2)
    test_db.add(tag_1)
    test_db.add(tag_2)
    test_db.add(device_1)
    test_db.add(device_2)

    test_db.commit()

    yield test_db
