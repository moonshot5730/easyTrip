from fastapi import APIRouter, Query, HTTPException
from langchain_core.messages import HumanMessage
from starlette.responses import StreamingResponse, JSONResponse

from app.cognitive_service.agent_core.manage_graph import agent_app
from app.cognitive_service.agent_core.graph_event import \
    handle_streaming_event
from app.core.logger.logger_config import get_logger
from app.internal.services.trip_planner_langgraph_service import fetch_graph_state_by_session, trip_plan_agent_chat
from app.schemes.agent_scheme import ChatRequest
from shared.event_constant import (CHAIN_START, DATA_TAG, END_MSG,
                                   SPLIT_PATTEN, STEP_TAG)

logger = get_logger()
trip_plan_router = APIRouter(prefix="/trip/plan", tags=["trip plan agent"])


@trip_plan_router.get("/langgraph/state")
def get_graph_state(session_id: str = Query(..., description="세션 ID")):
    logger.info(f"랭그래프 세션 조회 호출. 세션 정보 : {session_id}")

    return fetch_graph_state_by_session(session_id = session_id)


@trip_plan_router.post("/astream-event")
async def trip_plan(chat_request: ChatRequest):
    logger.info(f"여행 계획 이벤트 API 호출. 사용자 요청 정보 : {chat_request}")

    return await trip_plan_agent_chat(chat_request)


@trip_plan_router.get("/")
async def read_root():
    return {"message": "여행 계획을 세워주는 멀티 에이전트서버는 잘 동작하고 있습니다."}
