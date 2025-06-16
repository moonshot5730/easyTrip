from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.lifecycle.env_setting import load_env
from app.core.lifecycle.validate_key_setting import validate_llm_keys


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_env()
    validate_llm_keys()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "FastAPI is running with required API keys"}
