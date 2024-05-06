import logging
from contextvars import ContextVar

import sqlalchemy.exc as exc
from sqlalchemy.orm import Session

from chocolate_smart_home import models
from chocolate_smart_home.database import SessionLocal, engine


logger = logging.getLogger()

try:
    models.Base.metadata.create_all(bind=engine)
except exc.SQLAlchemyError as e:
    logger.error(e)


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

db_session: ContextVar[Session] = ContextVar('db_session', default=next(get_db()))
