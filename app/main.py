import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI

from app.core.config import load_env


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_env()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "FastAPI is running with required API keys"}
