from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    return {}


@router.get("/get_controllers_data/")
async def get_controllers_data():
    return {}


@router.post("/update_controller_data/")
async def update_controller_data():
    return {}


@router.get("/get_aggregate_controllers/")
async def get_aggregate_controllers():
    return {}


@router.get("/get_spaces/")
async def get_rooms():
    return {}
