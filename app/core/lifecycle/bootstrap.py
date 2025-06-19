from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.api.v1.planner_endpoints import trip_plan_router
from app.core.lifecycle.env_setting import load_env
from app.core.lifecycle.validate_key_setting import validate_env_keys

allowed_origins = [
    "http://localhost:8501",  # 개발용
    "http://127.0.0.1:8501",
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    load_env()
    validate_env_keys()
    # validate_llm_keys()  서버 시작할 때 의존하고 있는 llm_key가 유효한지 확인하는 테스트.
    yield

    # 서버 종료 로직


def boostrap():

    app = FastAPI(
        title="여행 계획을 세워주는 멀티 에이전트 시스템",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.include_router(trip_plan_router)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,  # 또는 allow_origins=["*"] (개발용)
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
