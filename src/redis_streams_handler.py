import asyncio
import logging
import os
from redis.asyncio import Redis

from src.SingletonMeta import SingletonMeta

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class RedisStreamsHandlerCSMBackend(metaclass=SingletonMeta):
    BACKEND_STREAM_NAME = os.getenv("BACKEND_STREAM_NAME")

    def __init__(self):
        self.redis_client = Redis(host=os.getenv("REDIS_HOST"), decode_responses=True)

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

    async def handle_message(self, move_data: dict):
        pass
