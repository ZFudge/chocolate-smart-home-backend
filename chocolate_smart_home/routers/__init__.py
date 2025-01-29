from .devices import device_router
from .frontend import router as frontend_router
from .tags import tags_router
from .websocket import ws_router

APP_ROUTERS = (
    device_router,
    frontend_router,
    tags_router,
    ws_router,
)
