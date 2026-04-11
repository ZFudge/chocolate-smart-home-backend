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
        logger.warning("No virtual client module found")
        return False

    if not hasattr(vcs_module, "seeds"):
        logger.warning(f"No seeds list found in {vcs_module.__name__}")
        return False
    elif not isinstance(vcs_module.seeds, (list, tuple)):
        logger.warning(f"seeds is not an iterable of dicts in {vcs_module.__name__}")
        return False

    if hasattr(vcs_module, "compose_state_as_msg"):
        if not callable(vcs_module.compose_state_as_msg):
            logger.warning(
                f"compose_state_as_msg must be a callable: {vcs_module.__name__}"
            )
            return False
        else:
            sig = signature(vcs_module.compose_state_as_msg)
            if (
                len(sig.parameters) != 1
                or "seed" not in sig.parameters
                or sig.return_annotation is not str
            ):
                logger.warning(
                    "The signature of parse_payload must be: (seed: dict) -> str. "
                    f"Received {sig}"
                )
                return False

    if hasattr(vcs_module, "parse_payload"):
        if not callable(vcs_module.parse_payload):
            logger.warning(f"parse_payload must be a callable: {vcs_module.__name__}")
            return False
        else:
            sig = signature(vcs_module.parse_payload)
            annotation = sig.return_annotation.__args__
            if (
                len(sig.parameters) != 1
                or "payload" not in sig.parameters
                or sig.parameters["payload"].annotation is not str
                or type(annotation) not in (list, tuple)
                or len(annotation) != 2
            ):
                logger.warning(
                    "Expecting parse_payload function to accepts a single argument, "
                    '"payload" annotated as a str type, and a return annotation '
                    f"of type list or tuple, with a length of 2 -> {sig}"
                )
                return False

    return True
