# seed data for virtual clients, to simulate
# Leonardo Virtual Client controllers during development

import logging

logger = logging.getLogger(__name__)

seeds = [
    dict(name="Leonardo Virtual Client 0"),
    dict(name="Leonardo Virtual Client 1"),
    dict(name="Leonardo Virtual Client 2"),
]


def translate_vc_dict_to_mqtt_msg(seed: dict) -> str:
    """Mocks the controller state expected by the CSM server"""
    msg_values = [
        # Add configs
        seed["mqtt_id"],
        seed["device_type_name"],
        seed["name"],
    ]

    msg_values = map(str, msg_values)

    return ",".join(msg_values)


def parse_payload(payload: str) -> tuple[None, None]:
    """Accepts payload from virtual client. Returns None for key and value."""
    logger.info(f"Received payload: {payload}")
    return None, None
