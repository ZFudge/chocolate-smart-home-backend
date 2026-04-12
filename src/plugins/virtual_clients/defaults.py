def default_compose_outgoing_msg(seed: dict) -> str:
    """Handles common configurations (mqtt id, device type name, remote name)
    providing a common root message for stateful devices, an the entirety of the device state for stateless devices.
    """
    msg_values = [
        seed["mqtt_id"],
        seed["device_type_name"],
        seed["name"],
    ]

    msg_values = map(str, msg_values)

    return ",".join(msg_values)


def default_parse_incoming_payload(payload: str) -> tuple[str, str]:
    """Used by stateless devices."""
    return "last_payload", payload
