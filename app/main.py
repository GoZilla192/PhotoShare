from fastapi import FastAPI
from app.routers.auth import router as auth_router

from app.routers.admin import router as admin_router
from app.routers.photos import router as photos_router


app = FastAPI()
app.include_router(admin_router)
app.include_router(photos_router)
app.include_router(auth_router)
