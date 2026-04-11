import importlib
import logging
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

    if not hasattr(vcs_module, "translate_vc_dict_to_mqtt_msg"):
        logger.warning(
            f"No translate_vc_dict_to_mqtt_msg function found in {vcs_module.__name__}"
        )
        return False
    elif not callable(vcs_module.translate_vc_dict_to_mqtt_msg):
        logger.warning(
            f"translate_vc_dict_to_mqtt_msg must be a callable: {vcs_module.__name__}"
        )
        return False

    if not hasattr(vcs_module, "parse_payload"):
        logger.warning(f"No parse_payload function found in {vcs_module.__name__}")
        return False
    elif not callable(vcs_module.parse_payload):
        logger.warning(f"parse_payload must be a callable: {vcs_module.__name__}")
        return False

    return True
