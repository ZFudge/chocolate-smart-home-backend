import logging

from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session

from .models import Palette

db_session: Session | None = None

plugin_router = APIRouter(prefix="/neo_pixel")

logger = logging.getLogger(__name__)


@plugin_router.get("/palettes/")
def get_palettes():
    global db_session
    if db_session is None:
        raise HTTPException(status_code=500, detail="Database not initialized.")
    try:
        return db_session.query(Palette).all()
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Error getting palettes.")
