import logging
import sys
from contextvars import ContextVar

import sqlalchemy.exc as exc
from sqlalchemy.orm import Session

from chocolate_smart_home.database import Base, SessionLocal, engine


logger = logging.getLogger()


try:
    Base.metadata.create_all(bind=engine)
except exc.SQLAlchemyError as e:
    if "pytest" not in sys.modules:
        logger.error(e)
        raise


def db_closure():
    db: Session | None = None

    def db_func():
        nonlocal db
        if db is None:
            db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    return db_func


get_db = db_closure()

db_session: ContextVar[Session] = ContextVar("db_session", default=next(get_db()))
