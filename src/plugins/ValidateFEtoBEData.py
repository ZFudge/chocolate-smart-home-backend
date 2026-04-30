from typing import Any


class ValidateFEtoBEData:
    REQUIRED_KEYS = {"device_type_name", "mqtt_id", "name", "value"}

    def validate_msg_data(self, msg_data: dict | Any) -> bool:
        if not isinstance(msg_data, dict):
            raise TypeError(f"Invalid message type: {type(msg_data)}")
        if not self.REQUIRED_KEYS.issubset(msg_data.keys()):
            raise ValueError(
                "data must contain device_type_name, mqtt_id, name, and value. "
                f"Missing keys: {sorted(self.REQUIRED_KEYS.difference(msg_data.keys()))}"
            )
        return True
