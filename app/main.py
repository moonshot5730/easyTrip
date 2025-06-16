from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.lifecycle.env_setting import load_env
from app.core.lifecycle.validate_key_setting import (validate_env_keys,
                                                     validate_llm_keys)


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_env()
    validate_env_keys()
    # validate_llm_keys()  서버 시작할 때 의존하고 있는 llm_key가 유효한지 확인하는 테스트.
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "FastAPI is running with required API keys"}
