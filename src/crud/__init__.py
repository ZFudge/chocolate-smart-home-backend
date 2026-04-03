from src.crud.device_types import create_device_type, get_device_type_by_name
from src.crud.devices import (
    delete_device,
    get_device_by_id,
    get_devices,
    patch_device,
)
from src.crud.tags import (
    create_tag,
    delete_tag,
    get_tag_by_id,
    get_tag_by_name,
    get_tags_by_ids,
    get_tags,
    patch_tag,
)

__all__ = [
    "create_device_type",
    "create_tag",
    "delete_device",
    "delete_tag",
    "get_device_by_id",
    "get_device_type_by_name",
    "get_devices",
    "get_tag_by_id",
    "get_tag_by_name",
    "get_tags_by_ids",
    "get_tags",
    "patch_device",
    "patch_tag",
]
