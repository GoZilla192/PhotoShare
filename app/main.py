from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.photos import router as photos_router
from app.routers.qr import qr_router
from app.routers.tags import tags_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(photos_router)
app.include_router(qr_router)
app.include_router(tags_router)