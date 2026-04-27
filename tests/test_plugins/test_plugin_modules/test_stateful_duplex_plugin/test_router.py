from fastapi.testclient import TestClient

from src.plugins import PluginsManager


def test_stateful_duplex_plugin_router_example_endpoint(
    stateful_duplex_plugin_path, test_app
):
    PluginsManager.check_router(stateful_duplex_plugin_path)
    test_app.include_router(PluginsManager.ROUTERS[0])
    client = TestClient(test_app)
    resp = client.get("/stateful_duplex_plugin/example_empty_endpoint/")
    assert resp.status_code == 200
    assert resp.json() == []


def test_stateful_duplex_plugin_router_get_properties(
    stateful_duplex_plugin_path, test_app, empty_test_db
):
    PluginsManager.check_extra_models(stateful_duplex_plugin_path)
    PluginsManager.check_db_seeding(stateful_duplex_plugin_path)
    PluginsManager.check_router(stateful_duplex_plugin_path)
    test_app.include_router(PluginsManager.ROUTERS[0])
    client = TestClient(test_app)
    resp = client.get("/stateful_duplex_plugin/properties/")
    assert resp.status_code == 200
    assert resp.json() == [
        {"id": 1, "name": "property_1", "value": "on"},
        {"id": 2, "name": "property_2", "value": "7"},
        {"id": 3, "name": "property_3", "value": "cabbage"},
    ]
