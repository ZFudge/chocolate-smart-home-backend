import logging

from .ValidateFEtoBEData import ValidateFEtoBEData

logger = logging.getLogger()


class BaseServerToControllerMessenger(ValidateFEtoBEData):
    def compose_controller_msg(self, msg_data: dict, *args, **kwargs) -> str:
        """Implemented at the plugin level.
        Defined here to allow compatibility with controllers that accept messages without formatting or validation
        """
        self.validate_msg_data(msg_data)
        return self._compose_param(msg_data["name"], msg_data["value"])

    @staticmethod
    def _compose_param(key: str, val: str) -> str:
        return f"{key}={val};"
