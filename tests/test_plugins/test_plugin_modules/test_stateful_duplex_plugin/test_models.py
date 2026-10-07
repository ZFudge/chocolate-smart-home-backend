from src.database import Base
from src.plugins import PluginsManager


def test_stateful_duplex_plugin_models_import_adds_extra_models(
    stateful_duplex_plugin_path, empty_test_db
):
    PluginsManager.check_extra_models(stateful_duplex_plugin_path)
    assert "properties" in Base.metadata.tables
    assert "readings" in Base.metadata.tables
