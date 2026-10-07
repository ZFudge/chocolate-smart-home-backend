from src.plugins.virtual_clients import VirtualClientsManager


def test_VirtualClientsManager_singleton():
    assert VirtualClientsManager() is VirtualClientsManager()
