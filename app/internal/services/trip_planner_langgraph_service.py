from fastapi import HTTPException
from langchain_core.messages import HumanMessage, BaseMessage
from starlette.responses import JSONResponse, StreamingResponse

from app.cognitive_service.agent_core.manage_graph import agent_app
from app.cognitive_service.agent_core.graph_event import handle_streaming_event
from app.core.logger.logger_config import api_logger
from app.schemes.agent_scheme import ChatRequest
from shared.event_constant import STEP_TAG, END_MSG, SPLIT_PATTEN, SSETag



def fetch_graph_state_by_session(session_id: str) -> JSONResponse:
    state = agent_app.get_state(checkpointer_config(session_id))
    if state is None:
        raise HTTPException(status_code=404, detail=f"{session_id} 해당 세션 상태가 없습니다.")

    values = state.values.copy()

    messages = values.get("messages", [])
    values["messages"] = [
        m.content if isinstance(m, BaseMessage) else str(m) for m in messages
    ]

    return JSONResponse(content=values)


def checkpointer_config(session_id):
    return {"configurable": {"thread_id": session_id}}


async def trip_plan_agent_chat(chat_request: ChatRequest) -> StreamingResponse:
    user_message = HumanMessage(**chat_request["message"])

    streaming_events = agent_app.astream_events(
        # input={"messages": [user_message]},
        input={"user_query": user_message.content},
        version="v2",
        stream_mode=["updates"],
        config=checkpointer_config(chat_request["session_id"]),
    )

    async def event_stream():
        async for event in streaming_events:
            for sse_message in handle_streaming_event(event):
                yield sse_message
        yield f"{SSETag.CHAT} __END__\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")