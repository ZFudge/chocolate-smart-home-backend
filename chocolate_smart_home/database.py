from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DB_URL = "postgresql://"
PG_USER = "zfudge"
PG_PW = "mysecretpassword"
PG_HOST = "127.0.0.1"
PG_PORT = 5432
PG_DATABASE = "CHOCOLATE_SMART_HOME"
PG_DATABASE = "chocolate"

SQLALCHEMY_DATABASE_URL = f"{DB_URL}{PG_USER}:{PG_PW}@{PG_HOST}/{PG_DATABASE}"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
