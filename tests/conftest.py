from contextvars import ContextVar

from sqlalchemy.orm import Session, sessionmaker
import pytest

from chocolate_smart_home import models
from chocolate_smart_home.database import Base
from chocolate_smart_home.dependencies import db_session, get_db, engine
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
    db_session.get().query(models.DeviceType).delete()
    db_session.get().commit()

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def populated_test_db(empty_test_db):
    device_type_1 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_1")
    device_type_2 = models.DeviceType(name="TEST_DEVICE_TYPE_NAME_2")
    empty_test_db.add(device_type_1)
    empty_test_db.add(device_type_2)

    device_1 = models.Device(
        mqtt_id=111,
        device_type=device_type_1,
        remote_name="Remote Name 1",
        name="Name 1",
        online=True,
    )
    device_2 = models.Device(
        mqtt_id=222,
        device_type=device_type_2,
        remote_name="Remote Name 2",
        name="Name 2",
        online=False,
    )
    empty_test_db.add(device_1)
    empty_test_db.add(device_2)

    empty_test_db.commit()

    yield empty_test_db
