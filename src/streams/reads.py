import asyncio
import logging

from src.dependencies import redis_session
from src.pubsub.comm_funcs import request_all_devices_data
from . import stream_names

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


async def handle_message(message_data: dict):
    logger.info(f"Handling message: {message_data}")
    action = message_data.get("action")
    if action == "request_all_devices_data":
        request_all_devices_data()


async def handle_reads():
    last_id = "$"
    while True:
        try:
            messages = await redis_session.get().xread(
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
                        await handle_message(message_data)
        except KeyboardInterrupt:
            break
        except Exception as e:
            logger.error("Error handling messages: %s" % e)
            await asyncio.sleep(1)
