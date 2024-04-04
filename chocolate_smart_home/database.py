import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def get_sqlalchemy_database_url(
	db_url=None,
	pg_user=None,
	pg_pw=None,
	pg_host=None,
	pg_port=None,
	pg_database=None,
):
	if db_url is None:
		db_url = os.environ.get("DB_URL")
	if pg_user is None:
		pg_user = os.environ.get("PG_USER")
	if pg_pw is None:
		pg_pw = os.environ.get("PG_PW")
	if pg_host is None:
		pg_host = os.environ.get("DB_HOST", "127.0.0.1")
	if pg_port is None:
		pg_port = os.environ.get("DB_PORT", 5432)
	if pg_database is None:
		pg_database = "CHOCOLATE_SMART_HOME"

	return f"{db_url}{pg_user}:{pg_pw}@{pg_host}:{pg_port}/{pg_database}"


SQLALCHEMY_DATABASE_URL = get_sqlalchemy_database_url()

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
