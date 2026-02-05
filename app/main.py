from fastapi import FastAPI
from app.routers.auth import router as auth_router
from app.routers.photos import router as photos_router
from app.routers.comments import router as comments_router


app = FastAPI()
app.include_router(photos_router)
app.include_router(auth_router)
app.include_router(comments_router)
