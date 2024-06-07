from .devices import device_router
from .frontend import router as frontend_router
from .spaces import spaces_router

APP_ROUTERS = (
    device_router,
    frontend_router,
    spaces_router,
)
