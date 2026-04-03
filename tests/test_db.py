from src import database


def test_get_sqlalchemy_database_url(empty_test_db):
    sqlalchemy_database_url = database.get_sqlalchemy_database_url()
    expected_sqlalchemy_database_url = (
        "postgresql://testuser:testpw@csm-postgres-db-dev:5432/testdb"
    )
    assert sqlalchemy_database_url == expected_sqlalchemy_database_url
