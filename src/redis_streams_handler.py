import asyncio
import json
import logging
import os

from redis.asyncio import Redis
from src.schemas import DeviceFrontend as DeviceFrontendSchema
from src.SingletonMeta import SingletonMeta

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RedisStreamsHandlerCSMBackend(metaclass=SingletonMeta):
    BACKEND_STREAM_NAME = os.getenv("BACKEND_STREAM_NAME", "BACKEND_STREAM_NAME")
    WS_STREAM_NAME = os.getenv("WS_STREAM_NAME", "WS_STREAM_NAME")

    def __init__(self):
        self.redis_client = Redis(host=os.getenv("REDIS_HOST"), decode_responses=True)

    def is_connected(self):
        return (
            hasattr(self, 'redis_client') and
            isinstance(self.redis_client, Redis) and
            self.redis_client.connection is not None
        )

    async def handle_reads(self):
        last_id = "$"
        while True:
            try:
                messages = await self.redis_client.xread(
                    {RedisStreamsHandlerCSMBackend.BACKEND_STREAM_NAME: last_id},
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
                            await self.handle_message(message_data)
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error("Error handling messages: %s" % e)
                await asyncio.sleep(1)

    async def handle_message(self, message_data: dict):
        pass

    async def send_to_ws_service(self, device_data: DeviceFrontendSchema):
        data = device_data.model_dump()
        message_data = dict(message=json.dumps(data))
        await self.redis_client.xadd(
            RedisStreamsHandlerCSMBackend.WS_STREAM_NAME, message_data
        )
