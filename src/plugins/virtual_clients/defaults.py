def default_compose_state_as_msg(seed: dict) -> str:
    """Mocks the controller state expected by the CSM server"""
    msg_values = [
        # Add configs
        seed["mqtt_id"],
        seed["device_type_name"],
        seed["name"],
    ]

    msg_values = map(str, msg_values)

    return ",".join(msg_values)


def default_parse_payload(payload: str) -> tuple[None, None]:
    """Accepts payload from virtual client. Returns None for key and value."""
    return None, None
