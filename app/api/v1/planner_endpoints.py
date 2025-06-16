import asyncio

from fastapi import APIRouter
from starlette.responses import StreamingResponse

from app.cognitive_service.events.sse_langchain_handler import PrintDebugHandler
from app.external.openai.openai_client import precise_llm_nano
from app.internal.use_case.trip_plan_agent_use_case import stream_trip_plan
from app.schemes.chat_schemes import ChatRequest

trip_plan_router = APIRouter(prefix="/trip/plan", tags=["trip plan agent"])

@trip_plan_router.post("/test/stream")
async def trip_plan(chat_request: ChatRequest):
    event_generator = await stream_trip_plan(chat_request)

    return StreamingResponse(
        event_generator,
        media_type="text/event-stream"
    )

@trip_plan_router.post("/debug/stream")
async def trip_plan_debug(chat_request: ChatRequest):
    await precise_llm_nano.ainvoke("서울 당일치기 여행지 추천해줘", callbacks=[PrintDebugHandler])

@trip_plan_router.get("/")
async def read_root():
    return {"message": "멀티 에이전트 시스템이 잘 동작하고 있습니다."}