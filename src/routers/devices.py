import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import NoResultFound

from src import crud, schemas

logger = logging.getLogger(__name__)

device_router = APIRouter(prefix="/devices")


@device_router.get("/", response_model=tuple[schemas.DeviceFrontend, ...])
def get_devices():
    try:
        devices = crud.get_devices()
        devices_list = []
        for d in devices:
            plugin = d.get("plugin")
            if plugin is not None:
                del plugin["id"]
                del plugin["mqtt_id"]

            tag_ids = d.get("tag_ids")
            if tag_ids:
                # tag_ids is JSON cast to string
                tag_ids = eval(tag_ids)

            devices_list.append(
                schemas.DeviceFrontend(
                    mqtt_id=d["mqtt_id"],
                    name=d["name"],
                    remote_name=d["remote_name"],
                    device_type_name=d["device_type_name"],
                    tags=tag_ids,
                    reboots=d["reboots"],
                    last_seen=str(d["last_seen"]) if d.get("last_seen") else None,
                    last_update_sent=(
                        str(d["last_update_sent"])
                        if d.get("last_update_sent")
                        else None
                    ),
                    plugin=plugin,
                )
            )
        return tuple(devices_list)
    except Exception as e:
        logger.error("Error getting devices: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get devices.")


@device_router.get("/{mqtt_id}", response_model=schemas.DeviceFrontend | None)
def get_device_by_id(mqtt_id: int):
    try:
        device = crud.get_device_by_id(mqtt_id)
        if device is None:
            return None
        return schemas.device_mod_obj_to_frontend_schema(device)
    except Exception as e:
        logger.error("Error getting device with mqtt id %s: %s", mqtt_id, e)
        raise HTTPException(
            status_code=500, detail="Failed to get device with mqtt id %s." % mqtt_id
        )


@device_router.delete("/{mqtt_id}", response_model=None, status_code=204)
async def delete_device(mqtt_id: int):
    try:
        crud.delete_device(mqtt_id)
        # asyncio.create_task(broadcast_deleted_device(mqtt_id))
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=str(e.args[0]))
    except Exception as e:
        logger.error("Error deleting device with mqtt id %s: %s", mqtt_id, e)
        raise HTTPException(
            status_code=500, detail="Failed to delete device with mqtt id %s." % mqtt_id
        )


@device_router.patch("/", response_model=schemas.DeviceFrontend)
async def patch_device(patch_device: schemas.DevicePatch):
    try:
        patched_device = crud.patch_device(patch_device)
        if patched_device is None:
            raise ValueError
        # asyncio.create_task(dynamic_broadcast(patched_device))
        return schemas.device_mod_obj_to_frontend_schema(patched_device)
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=str(e.args[0]))
    except Exception as e:
        logger.error(
            "Error patching device with mqtt id %s: %s", patch_device.mqtt_id, e
        )
        raise HTTPException(
            status_code=500,
            detail="Failed to patch device with mqtt id %s." % patch_device.mqtt_id,
        )
