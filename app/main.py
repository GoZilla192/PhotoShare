from fastapi import FastAPI

from app.routers.photos import router as photos_router


app = FastAPI()
app.include_router(photos_router)
