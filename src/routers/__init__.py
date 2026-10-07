from .devices import device_router
from .misc import misc_router
from .tags import tags_router

APP_ROUTERS = (
    device_router,
    misc_router,
    tags_router,
)
