from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.cognitive_service.agent_langgraph.agent_state import ChatRequest
from app.cognitive_service.agent_langgraph.agent_graph import agent_app
from shared.event_constant import END_MSG, CHAIN_START, DATA_TAG, STEP_TAG, SPLIT_PATTEN
from app.core.logger.logger_config import get_logger

logger = get_logger()
trip_plan_router = APIRouter(prefix="/trip/plan", tags=["trip plan agent"])

@trip_plan_router.post("/astream-event")
async def trip_plan(chat_request: ChatRequest):
    logger.info(f"사용자 요청 정보 : {chat_request}")
    streaming_events = agent_app.astream_events(input=chat_request, version="v2")

    async def event_stream():
        async for se in streaming_events:
            print(se)
            kind = se["event"]
            name = se.get("name")
            data = se.get("data")

            if kind == CHAIN_START:
                if name == "intent_router":
                    yield f"{STEP_TAG} 사용자의 요청을 분석중입니다.{SPLIT_PATTEN}"

            if kind == "on_tool_start" and name == "intent_router":
                yield f"{STEP_TAG} 의도 분석 중...{SPLIT_PATTEN}"

            if kind == "on_tool_end" and name == "intent_router":
                action = data.get("output", {}).get("action", "unknown")
                yield f"{STEP_TAG} 의도 파악 완료 ({action}){SPLIT_PATTEN}"

            elif kind == "on_chat_model_stream":
                chunk = data["chunk"]
                content = chunk.content
                yield f"{DATA_TAG} {content}{SPLIT_PATTEN}"

        yield f"{STEP_TAG} {END_MSG}{SPLIT_PATTEN}"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@trip_plan_router.get("/")
async def read_root():
    return {"message": "여행 계획을 세워주는 멀티 에이전트서버는 잘 동작하고 있습니다."}