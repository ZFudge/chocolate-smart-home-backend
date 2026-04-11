from src.plugins.virtual_clients.discover_virtual_clients import DiscoverVirtualClients


def test_discover_virtual_clients(mqtt_client):
    DiscoverVirtualClients().discover_virtual_clients()
