import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from .models import Properties

db: Session | None = None

plugin_router = APIRouter(prefix="/stateful_duplex_plugin")

logger = logging.getLogger(__name__)


@plugin_router.get("/example_empty_endpoint/")
def example_empty_endpoint():
    try:
        return []
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error in example empty endpoint.")


@plugin_router.get("/properties/")
def get_properties():
    global db
    if db is None:
        raise HTTPException(status_code=500, detail="Database not initialized.")
    try:
        return db.query(Properties).all()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error getting properties.")
