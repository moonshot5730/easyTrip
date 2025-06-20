from fastapi import APIRouter, Query, HTTPException
from langchain_core.messages import HumanMessage
from starlette.responses import StreamingResponse, JSONResponse

from app.cognitive_service.agent_langgraph.agent_graph import agent_app
from app.cognitive_service.agent_langgraph.agent_graph_event import \
    handle_streaming_event
from app.core.logger.logger_config import get_logger
from app.schemes.agent_scheme import ChatRequest
from shared.event_constant import (CHAIN_START, DATA_TAG, END_MSG,
                                   SPLIT_PATTEN, STEP_TAG)

logger = get_logger()
trip_plan_router = APIRouter(prefix="/trip/plan", tags=["trip plan agent"])


@trip_plan_router.get("/langgraph/state")
def get_graph_state(session_id: str = Query(..., description="세션 ID")):
    config = {"configurable": {"thread_id": session_id}}
    print(f"세션 정보 : {session_id}")
    try:
        # 저장된 상태 조회
        state = agent_app.get_state(config)
        if state is None:
            raise HTTPException(status_code=404, detail="해당 세션 상태가 없습니다.")

        values = state.values.copy()
        print("state 정보 ", state)

        # ✅ messages 처리: content만 추출
        messages = values.get("messages", [])
        values["messages"] = [
            getattr(m, "content", str(m)) for m in messages
        ]
        return JSONResponse(content=values)

    except Exception as e:
        print("예외 정보: ", str(e))
        raise HTTPException(status_code=500, detail=str(e))

@trip_plan_router.post("/astream-event")
async def trip_plan(chat_request: ChatRequest):
    logger.info(f"사용자 요청 정보 : {chat_request}")

    user_message = HumanMessage(**chat_request["message"])

    streaming_events = agent_app.astream_events(
        input={"messages": [user_message]},
        version="v2",
        stream_mode=["updates"],
        config={"configurable": {"thread_id": chat_request["session_id"]}},
    )

    async def event_stream():
        async for event in streaming_events:
            for sse_messge in handle_streaming_event(event):
                yield sse_messge
            # kind = event["event"]
            # name = event.get("name")
            # data = event.get("data")
            #
            # if kind == CHAIN_START:
            #     if name == "intent_router":
            #         yield f"{STEP_TAG} 사용자의 요청을 분석중입니다.{SPLIT_PATTEN}"
            #
            # if kind == "on_tool_start" and name == "intent_router":
            #     yield f"{STEP_TAG} 의도 분석 중...{SPLIT_PATTEN}"
            #
            # if kind == "on_tool_end" and name == "intent_router":
            #     action = data.get("output", {}).get("action", "unknown")
            #     yield f"{STEP_TAG} 의도 파악 완료 ({action}){SPLIT_PATTEN}"
            #
            # elif kind == "on_chat_model_stream":
            #     chunk = data["chunk"]
            #     content = chunk.content
            #     yield f"{DATA_TAG} {content}{SPLIT_PATTEN}"

        yield f"{STEP_TAG} {END_MSG}{SPLIT_PATTEN}"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@trip_plan_router.get("/")
async def read_root():
    return {"message": "여행 계획을 세워주는 멀티 에이전트서버는 잘 동작하고 있습니다."}
