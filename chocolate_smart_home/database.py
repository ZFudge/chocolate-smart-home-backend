import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = os.environ.get("DB_URL")
PG_USER = os.environ.get("PG_USER")
PG_PW = os.environ.get("PG_PW")
PG_HOST = os.environ.get("DB_HOST", "127.0.0.1")
PG_PORT = os.environ.get("DB_PORT", 5432)
PG_DATABASE = "CHOCOLATE_SMART_HOME"

SQLALCHEMY_DATABASE_URL = f"{DB_URL}{PG_USER}:{PG_PW}@{PG_HOST}/{PG_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
