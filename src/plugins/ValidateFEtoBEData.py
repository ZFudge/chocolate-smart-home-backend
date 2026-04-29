class ValidateFEtoBEData:
    def validate_msg_data(self, msg_data: dict) -> bool:
        if not isinstance(msg_data, dict):
            raise TypeError(f"Invalid message type: {type(msg_data)}")
        if msg_data.keys().isdisjoint(["device_type_name", "mqtt_id", "name", "value"]):
            raise ValueError(
                "data must contain device_type_name, mqtt_id, name, and value"
            )
        return True
