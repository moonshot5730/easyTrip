import asyncio

from fastapi import APIRouter

from app.schemes.chat_schemes import ChatRequest

trip_plan_router = APIRouter(prefix="/trip/plan", tags=["trip plan agent"])

@trip_plan_router.post("/test/stream")
async def trip_plan(chat_request: ChatRequest):
    # event_generator = await stream_trip_plan(chat_request)
    #
    # return StreamingResponse(
    #     event_generator,
    #     media_type="text/event-stream"
    # )



@trip_plan_router.get("/")
async def read_root():
    return {"message": "여행 계획을 세워주는 멀티 에이전트서버는 잘 동작하고 있습니다."}