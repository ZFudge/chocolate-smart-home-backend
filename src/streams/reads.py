import asyncio
import logging

from . import stream_names
from src import dependencies
from src.handle_device_update import handle_device_update

logger = logging.getLogger(__name__)


def _get_handle_reads():
    last_id = "$"

    async def _handle_reads():
        nonlocal last_id
        messages = await dependencies.redis_session.get().xread(
            {stream_names.BACKEND_STREAM_NAME: last_id},
            count=1,
            block=1000,
        )
        if messages:
            logger.info(f"Received messages: {messages}")
            for stream_name, message_list in messages:
                logger.info(f"Stream name: {stream_name}")
                for message_id, message_data in message_list:
                    logger.info(
                        f"Received message ID: {message_id}, Data: {message_data}"
                    )
                    last_id = message_id  # Update the last received ID
                    await handle_device_update(message_data)

    return _handle_reads


async def handle_reads():  # pragma: no cover
    _handle_reads = _get_handle_reads()
    while True:
        try:
            await _handle_reads()
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error("Error handling messages: %s" % e)
            await asyncio.sleep(1)
