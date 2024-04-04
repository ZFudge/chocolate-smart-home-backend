from contextvars import ContextVar
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
import pytest

from chocolate_smart_home import models
from chocolate_smart_home.database import Base, get_sqlalchemy_database_url
from chocolate_smart_home.dependencies import db_session, get_db
from chocolate_smart_home.main import app


SQLALCHEMY_DATABASE_URL = get_sqlalchemy_database_url(
    pg_user="testuser",
    pg_pw="testpw",
    pg_port=15432,
    pg_database="testdb",
)
engine = create_engine(SQLALCHEMY_DATABASE_URL)

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
def test_database():
    override_get_db = db_closure()
    app.dependency_overrides[get_db] = override_get_db

    override_db_session: ContextVar[Session] = ContextVar(
        'db_session',
        default=next(override_get_db())
    )
    db_session.set(next(override_get_db()))
    app.dependency_overrides[db_session] = override_db_session

    yield db_session.get()

    db_session.get().query(models.Device).delete()
    db_session.get().query(models.DeviceType).delete()
    db_session.get().commit()
