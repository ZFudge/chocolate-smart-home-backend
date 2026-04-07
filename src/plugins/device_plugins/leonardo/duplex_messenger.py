import logging

from .commands import COMMANDS

logger = logging.getLogger(__name__)


class LeonardoDuplexMessenger:
    """Adapts data between app and MQTT."""

    @staticmethod
    def compose_msg(msg: dict) -> str:
        if not isinstance(msg, dict):
            raise ValueError(f"Invalid message type: {type(msg)}")
        if "command" not in msg:
            raise ValueError(f"Missing command in message: {msg}")
        if msg["command"] not in COMMANDS:
            raise ValueError(
                f"Invalid command: {msg['command']}. Valid commands are: {COMMANDS}"
            )
        return msg["command"]


# Alias messenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["leonardo"] dict.
DuplexMessenger = LeonardoDuplexMessenger
