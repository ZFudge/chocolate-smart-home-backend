from .commands import COMMANDS


class LeonardoServerToControllerMessenger:
    """Adapts data between app and MQTT."""

    @staticmethod
    def compose_controller_msg(msg: dict) -> str:
        if not isinstance(msg, dict):
            raise ValueError(f"Invalid message type: {type(msg)}")
        if "command" not in msg:
            raise ValueError(f"Missing command in message: {msg}")
        if msg["command"] not in COMMANDS:
            raise ValueError(
                f"Invalid command: {msg['command']}. Valid commands are: {COMMANDS}"
            )
        return msg["command"]


# Alias messenger for discovery.
ServerToControllerMessenger = LeonardoServerToControllerMessenger
