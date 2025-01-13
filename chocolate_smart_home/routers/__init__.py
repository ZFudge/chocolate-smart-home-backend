from .devices import device_router
from .frontend import router as frontend_router
from .spaces import spaces_router
from .websocket import ws_router

APP_ROUTERS = (
    device_router,
    frontend_router,
    spaces_router,
    ws_router,
)
