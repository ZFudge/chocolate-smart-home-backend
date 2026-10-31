import datetime as dt
from unittest.mock import AsyncMock

import pytest

from src import utils
from src.models.device import Device


@pytest.mark.asyncio
async def test_is_not_online():
    date = dt.datetime.fromisoformat("2025-01-01 00:00:00.000000")
    device = Device(
        mqtt_id=123,
        last_seen=date - dt.timedelta(minutes=1) - dt.timedelta(seconds=1),
        last_update_sent=date,
    )
    assert not await utils.is_online(device)


@pytest.mark.asyncio
async def test_is_online(mocked_redis_session):
    date = dt.datetime.fromisoformat("2025-01-01 00:00:00.000000")
    device = Device(
        mqtt_id=123,
        last_seen=date,
        last_update_sent=date - dt.timedelta(minutes=1, seconds=1),
    )
    is_online = await utils.is_online(device)
    assert is_online is True


@pytest.mark.asyncio
async def test_get_request_all_device_data_last_sent_as_dt(
    mocked_redis_session, test_request_all_device_data_last_sent_key
):
    await utils.get_request_all_device_data_last_sent_as_dt()
    mocked_redis_session.get.assert_called_once_with(
        test_request_all_device_data_last_sent_key
    )


@pytest.mark.asyncio
async def test_get_request_all_device_data_last_sent_as_dt_returns_datetime(
    mocked_redis_session,
):
    JAN_1ST_2026_TIMESTAMP = 1767254400
    mocked_redis_session.get = AsyncMock(return_value=JAN_1ST_2026_TIMESTAMP)
    last_sent_datetime = await utils.get_request_all_device_data_last_sent_as_dt()
    expected_date = dt.datetime.fromtimestamp(JAN_1ST_2026_TIMESTAMP)
    assert last_sent_datetime == expected_date


@pytest.mark.asyncio
async def test_get_request_all_device_data_last_sent_as_dt_returns_None_on_exception(
    mocked_redis_session,
):
    invalid_timestamp = "cabbage"
    mocked_redis_session.get = AsyncMock(return_value=invalid_timestamp)
    assert await utils.get_request_all_device_data_last_sent_as_dt() is None


@pytest.mark.asyncio
async def test_set_request_all_device_data_last_sent_sets_timestamp(
    mocked_redis_session,
    test_request_all_device_data_last_sent_key,
):
    last_sent_dt = dt.datetime.fromisoformat("2026-01-01T00:00:00")
    await utils.set_request_all_device_data_last_sent(last_sent_dt)
    mocked_redis_session.set.assert_called_once_with(
        test_request_all_device_data_last_sent_key, last_sent_dt.timestamp()
    )


@pytest.mark.asyncio
async def test_set_request_all_device_data_last_sent_raises_typerror():
    with pytest.raises(TypeError):
        await utils.set_request_all_device_data_last_sent("not a datetime object")
