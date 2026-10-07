from . import utils


class ServerToControllerMessenger:
    def compose_controller_msg(self, msg_data: dict) -> str | None:
        """Compose outgoing message to be published through MQTT."""
        default_message = super().compose_controller_msg(msg_data)
        if msg_data["name"] in ["on", "twinkle", "transform", "pir_armed"]:
            value = msg_data["value"]
            if isinstance(value, bool):
                value = str(int(value))
            return self._compose_param(msg_data["name"], value)
        elif msg_data["name"] in ["ms", "brightness", "pir_timeout"]:
            value = msg_data["value"]
            try:
                value = int(value)
            except ValueError:
                pass
            if isinstance(value, int):
                value = max(0, value)
                value = min(255, value)
            return self._compose_param(msg_data["name"], value)
        elif msg_data["name"] == "palette":
            # Palette is a list of 9 hex strings. Convert to a commas-separated list of 27 bytes
            # and embed in outgoing controller message
            palette_27_byte_str = utils.convert_9_hex_to_27_byte_str(msg_data["value"])
            return "palette={};".format(palette_27_byte_str)
        return default_message
