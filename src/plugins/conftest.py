from contextvars import ContextVar

import pytest
from sqlalchemy.exc import InternalError, ProgrammingError
from sqlalchemy.orm import Session, sessionmaker

from src import models, SingletonMeta
from src.database import Base
from src.dependencies import db_session, engine, get_db
from src.main import app


@pytest.fixture(scope="function", autouse=True)
def singleton_instance_cleanup():
    SingletonMeta._SINGLETONS = {}
    yield


def db_closure():
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
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


@pytest.fixture(autouse=True)
def clear_test_db():
    yield
    try:
        db_session.get().query(models.device_tags).delete()
        db_session.get().query(models.Device).delete()
        db_session.get().query(models.Tag).delete()
        db_session.get().query(models.DeviceType).delete()
        db_session.get().commit()
        Base.metadata.drop_all(bind=engine)
    except (ProgrammingError, InternalError):
        pass


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
