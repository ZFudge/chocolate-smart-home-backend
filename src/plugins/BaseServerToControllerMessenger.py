import logging


logger = logging.getLogger()


class BaseServerToControllerMessenger:
    @staticmethod
    def compose_controller_msg(msg: str, *args, **kwargs):
        """Implemented at the plugin level.
        Defined here to allow compatibility with controllers that accept messages without formatting or validation
        """
        return msg

    @staticmethod
    def _compose_param(key: str, val: str) -> str:
        return f"&{key}={val}"
