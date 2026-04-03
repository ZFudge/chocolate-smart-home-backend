import asyncio
import logging
from typing import Tuple

from fastapi import APIRouter, HTTPException
from sqlalchemy.exc import NoResultFound

from src import crud, schemas
from src.websocket.dynamic_broadcast import broadcast_deleted_device, dynamic_broadcast

logger = logging.getLogger(__name__)

device_router = APIRouter(prefix="/devices")


@device_router.get("/", response_model=Tuple[schemas.DeviceFrontend, ...])
def get_devices():
    try:
        return tuple(
            [
                schemas.DeviceFrontend(
                    mqtt_id=device.mqtt_id,
                    remote_name=device.remote_name,
                    name=device.name,
                    device_type_name=device.device_type.name,
                    tags=[tag.id for tag in device.tags] if device.tags else None,
                    reboots=device.reboots,
                    last_seen=str(device.last_seen) if device.last_seen else None,
                    last_update_sent=(
                        str(device.last_update_sent)
                        if device.last_update_sent
                        else None
                    ),
                )
                for device in crud.get_devices()
                if device is not None
            ]
        )
    except Exception as e:
        logger.error("Error getting devices: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get devices.")


@device_router.get("/{mqtt_id}", response_model=schemas.DeviceFrontend | None)
def get_device_by_id(mqtt_id: int):
    try:
        device = crud.get_device_by_id(mqtt_id)
        if device is None:
            return None
        return schemas.DeviceFrontend(
            mqtt_id=mqtt_id,
            remote_name=device.remote_name,
            name=device.name,
            device_type_name=device.device_type.name,
            tags=[tag.id for tag in device.tags] if device.tags else None,
            reboots=device.reboots,
            last_seen=str(device.last_seen) if device.last_seen else None,
            last_update_sent=(
                str(device.last_update_sent) if device.last_update_sent else None
            ),
        )
    except Exception as e:
        logger.error("Error getting device with mqtt id %s: %s", mqtt_id, e)
        raise HTTPException(status_code=500, detail="Failed to get device.")


@device_router.delete("/{mqtt_id}", response_model=None, status_code=204)
async def delete_device(mqtt_id: int):
    try:
        crud.delete_device(mqtt_id)
        asyncio.create_task(broadcast_deleted_device(mqtt_id))
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=str(e.args[0]))
    except Exception as e:
        logger.error("Error deleting device with mqtt id %s: %s", mqtt_id, e)
        raise HTTPException(status_code=500, detail="Failed to delete device.")


@device_router.patch("/", response_model=schemas.DeviceFrontend)
async def patch_device(patch_device: schemas.DevicePatch):
    try:
        patched_device = crud.patch_device(patch_device)
        asyncio.create_task(dynamic_broadcast(patched_device))
        return schemas.DeviceFrontend(
            mqtt_id=patched_device.mqtt_id,
            remote_name=patched_device.remote_name,
            name=patched_device.name,
            device_type_name=patched_device.device_type.name,
            tags=(
                [tag.id for tag in patched_device.tags] if patched_device.tags else None
            ),
            reboots=patched_device.reboots,
            last_seen=(
                str(patched_device.last_seen) if patched_device.last_seen else None
            ),
            last_update_sent=(
                str(patched_device.last_update_sent)
                if patched_device.last_update_sent
                else None
            ),
        )
    except NoResultFound as e:
        raise HTTPException(status_code=500, detail=str(e.args[0]))
    except Exception as e:
        logger.error(
            "Error patching device with mqtt id %s: %s", patch_device.mqtt_id, e
        )
        raise HTTPException(status_code=500, detail="Failed to patch device.")
