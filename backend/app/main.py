from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import Base, engine
from app.models import *
from app.routers.auth_router import router as auth_router
from app.routers.pet_router import router as pet_router
from app.routers.task_router import router as task_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="TPU Pet API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth_router)
app.include_router(pet_router)
app.include_router(task_router)


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.mount("/", StaticFiles(directory="../frontend", html=True), name="frontend")
