from fastapi import FastAPI
from chocolate_smart_home.routers import frontend

app = FastAPI()

app.include_router(frontend.router)
