from datetime import datetime, timedelta

import pytest

from src import dependencies, utils
from src.models.device import Device


@pytest.mark.asyncio
async def test_is_not_online():
    date = datetime.fromisoformat("2025-01-01 00:00:00.000000")
    device = Device(
        mqtt_id=123,
        last_seen=date - timedelta(minutes=1) - timedelta(seconds=1),
        last_update_sent=date,
    )
    assert not await utils.is_online(device)


@pytest.mark.asyncio
async def test_is_online(monkeypatch):
    monkeypatch.setattr(
        dependencies,
        "REQUEST_ALL_DEVICE_DATA_LAST_SENT_KEY",
        "test_request_all_device_data_last_sent_key",
    )
    date = datetime.fromisoformat("2025-01-01 00:00:00.000000")
    device = Device(
        mqtt_id=123,
        last_seen=date,
        last_update_sent=date - timedelta(minutes=1, seconds=1),
    )
    assert await utils.is_online(device)
