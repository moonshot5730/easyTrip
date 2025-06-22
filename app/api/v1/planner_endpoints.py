from fastapi import APIRouter, Query, HTTPException
from starlette.responses import HTMLResponse

from app.core.constant.path_constant import SHARE_BASE_PATH
from app.core.logger.logger_config import get_logger
from app.internal.services.trip_planner_langgraph_service import (
    fetch_graph_state_by_session, trip_plan_agent_chat)
from app.schemes.agent_scheme import ChatRequest

logger = get_logger()
trip_plan_router = APIRouter(prefix="/trip/plan", tags=["trip plan agent"])


@trip_plan_router.get("/share/{file_name}", response_class=HTMLResponse)
async def serve_shared_plan(file_name: str):
    file_path = SHARE_BASE_PATH / file_name

    if not file_path.exists() or not file_path.suffix == ".html":
        raise HTTPException(status_code=404, detail="공유된 여행 계획 파일을 찾을 수 없습니다.")

    html_content = file_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)

@trip_plan_router.get("/langgraph/state")
def get_graph_state(session_id: str = Query(..., description="세션 ID")):
    logger.info(f"랭그래프 세션 조회 호출. 세션 정보 : {session_id}")

    return fetch_graph_state_by_session(session_id=session_id)


@trip_plan_router.post("/astream-event")
async def trip_plan(chat_request: ChatRequest):
    logger.info(f"여행 계획 이벤트 API 호출. 사용자 요청 정보 : {chat_request}")

    return await trip_plan_agent_chat(chat_request)


@trip_plan_router.get("/")
async def read_root():
    return {"message": "여행 계획을 세워주는 멀티 에이전트서버는 잘 동작하고 있습니다."}
