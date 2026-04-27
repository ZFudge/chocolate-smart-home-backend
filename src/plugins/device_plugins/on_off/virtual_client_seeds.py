import logging

logger = logging.getLogger("vcs")

seeds = [
    {
        "name": "On/Off Virtual Client 0",
        "on": False,
    },
    {
        "name": "On/Off Virtual Client 1",
        "on": True,
    },
    {
        "name": "On/Off Virtual Client 2",
        "on": False,
    },
    {
        "name": "On/Off Virtual Client 3",
        "on": True,
    },
    {
        "name": "On/Off Virtual Client 4",
        "on": True,
    },
    {
        "name": "On/Off Virtual Client 5",
        "on": False,
    },
    {
        "name": "On/Off Virtual Client 6",
        "on": True,
    },
]


def compose_outgoing_msg(vc_state: dict) -> str:
    """Mocks the controller state expected by the CSM server"""
    return str(int(vc_state["on"]))


def parse_incoming_payload(payload: str) -> tuple[str, str]:
    logger.info(f"Received on/off plugin virtual client payload: {payload}")
    return "on", payload
