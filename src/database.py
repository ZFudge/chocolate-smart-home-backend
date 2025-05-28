import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def get_sqlalchemy_database_url():
    db_url = os.environ.get("DB_URL", "postgresql://")
    user = os.environ.get("DB_USER", "testuser")
    pw = os.environ.get("DB_PW", "testpw")
    host = os.environ.get("DB_HOST", "127.0.0.1")
    port = os.environ.get("DB_PORT", 5432)
    db_name = os.environ.get("DB_NAME", "csm_db")

    return f"{db_url}{user}:{pw}@{host}:{port}/{db_name}"


SQLALCHEMY_DATABASE_URL = get_sqlalchemy_database_url()
print(f"SQLALCHEMY_DATABASE_URL: {SQLALCHEMY_DATABASE_URL}")

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
