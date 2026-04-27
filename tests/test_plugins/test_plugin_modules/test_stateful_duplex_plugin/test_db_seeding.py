from src.plugins import PluginsManager

from .stateful_duplex_plugin import models


def test_stateful_duplex_plugin_db_seeding(stateful_duplex_plugin_path, empty_test_db):
    PluginsManager.check_extra_models(stateful_duplex_plugin_path)
    PluginsManager.check_db_seeding(stateful_duplex_plugin_path)
    properties = empty_test_db.query(models.Properties).all()
    assert properties[0].name == "property_1"
    assert properties[1].name == "property_2"
    assert properties[2].name == "property_3"
    assert properties[0].value == "on"
    assert properties[1].value == "7"
    assert properties[2].value == "cabbage"
