import pytest

from src.database import Base
from src.dependencies import (
    db_session,
    engine,
)

from . import example_plugin


@pytest.fixture
def example_plugin_path():
    yield (__name__.rpartition(".")[0] + ".example_plugin")


@pytest.fixture(autouse=True)
def clear_plugin_table():
    yield
    try:
        db_session.get().query(example_plugin.Model.PluginModel).delete()
        db_session.get().commit()
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass
