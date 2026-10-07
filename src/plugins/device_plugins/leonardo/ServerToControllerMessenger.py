from typing import Any

from .commands import COMMANDS


class LeonardoServerToControllerMessenger:
    """Adapts data between app and MQTT."""

    def compose_controller_msg(self, msg_data: dict | Any) -> str:
        super().compose_controller_msg(msg_data)
        if msg_data["name"] != "command":
            raise ValueError(f"Missing command in message: {msg_data}")
        if msg_data["value"] not in COMMANDS:
            raise ValueError(
                f'Invalid command: "{msg_data['value']}". Valid commands are: {COMMANDS}'
            )
        return msg_data["value"]


# Alias messenger for discovery.
ServerToControllerMessenger = LeonardoServerToControllerMessenger
