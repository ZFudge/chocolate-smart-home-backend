# seed data for virtual clients, to simulate
# Leonardo Virtual Client controllers during development

import logging

logger = logging.getLogger("vcs")

seeds = [
    dict(name="Leonardo Virtual Client 0"),
    dict(name="Leonardo Virtual Client 1"),
    dict(name="Leonardo Virtual Client 2"),
]


def parse_incoming_payload(payload: str) -> tuple[None, None]:
    """Accepts payload from virtual client. Returns None for key and value."""
    logger.info(f"Received payload: {payload}")
    return None, None
