from typing import Dict

from chocolate_smart_home.plugins.base_duplex_messenger import BaseDuplexMessenger

ON_OFF_VALUE_LOOKUP = {
    "0": False,
    "1": True,
}

class OnOffDuplexMessenger(BaseDuplexMessenger):
    def parse_msg(self, raw_msg: str) -> Dict:
        """Parse message received from remote controller."""
        device_data, msg_seq = super().parse_msg(raw_msg)

        on_off_value: bool = next(msg_seq)
        device_data['on'] = ON_OFF_VALUE_LOOKUP[on_off_value]

        return device_data

    def compose_msg(self, on: bool) -> str:
        """Compose message for publish."""
        return "1" if on else "0"


# Alias OnOffDuplexMessenger for use in ..discovered_plugins.DISCOVERED_PLUGINS["on_off"] dict
DuplexMessenger = OnOffDuplexMessenger
