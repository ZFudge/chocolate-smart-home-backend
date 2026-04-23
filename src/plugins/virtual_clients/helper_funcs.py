import importlib
import logging
from inspect import signature
from types import ModuleType

logger = logging.getLogger(__name__)


def import_vcs_module(vcs_module_name: str) -> ModuleType | None:
    logger.info(f"Importing virtual client seeds module: {vcs_module_name}")
    try:
        vcs_module = importlib.import_module(vcs_module_name)
    except ImportError:
        logger.warning("No %s module found", vcs_module_name)
        return
    logger.info("Imported successfully.")
    return vcs_module


def validate_virtual_client_module(vcs_module: ModuleType | None) -> bool:
    if vcs_module is None:
        logger.warning("Virtual clients module not found")
        return False

    if not hasattr(vcs_module, "seeds"):
        logger.warning(f"{vcs_module.__name__}.seeds list not found.")
        return False
    elif not isinstance(vcs_module.seeds, (list, tuple)):
        logger.warning(f"{vcs_module.__name__}.seeds is not an iterable of dicts")
        return False

    if hasattr(vcs_module, "compose_outgoing_msg"):
        if not callable(vcs_module.compose_outgoing_msg):
            logger.warning(
                f"{vcs_module.__name__}.compose_outgoing_msg must be a callable"
            )
            return False
        else:
            sig = signature(vcs_module.compose_outgoing_msg)
            if (
                len(sig.parameters) != 1
                or "vc_state" not in sig.parameters
                or sig.return_annotation is not str
            ):
                logger.warning(
                    f"The signature of {vcs_module.__name__}.compose_outgoing_msg must be: (seed: dict) -> str. "
                    f"Received {sig}"
                )
                return False

    if hasattr(vcs_module, "parse_incoming_payload"):
        if not callable(vcs_module.parse_incoming_payload):
            logger.warning(
                f"{vcs_module.__name__}.parse_incoming_payload must be a callable"
            )
            return False
        else:
            sig = signature(vcs_module.parse_incoming_payload)
            annotation = sig.return_annotation
            if not hasattr(annotation, "__args__"):
                logger.warning(
                    f"{vcs_module.__name__}.parse_incoming_payload must return a tuple with length of 2"
                )
                return False
            if (
                len(sig.parameters) != 1
                or "payload" not in sig.parameters
                or sig.parameters["payload"].annotation is not str
                or type(annotation.__args__) is not tuple
                or len(annotation.__args__) != 2
            ):
                logger.warning(
                    f"Expecting {vcs_module.__name__}.parse_incoming_payload to accept a single argument, "
                    '"payload", annotated as a str type, with a return annotation '
                    f"of tuple with length of 2 -> {sig}"
                )
                return False

    return True
