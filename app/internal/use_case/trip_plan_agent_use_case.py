import asyncio
from asyncio import Queue

from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

from app.cognitive_service.agents.trip_plan_agent import agent
from app.cognitive_service.events.sse_langchain_handler import SSELangchainCallbackHandler
from app.core.logger.logger_config import get_logger
from app.schemes.chat_schemes import ChatRequest, Message

logger = get_logger()


async def stream_trip_plan(chat_request: ChatRequest):
    lc_messages = to_langchain_messages(chat_request.messages)

    queue = Queue()
    handler = SSELangchainCallbackHandler(queue)

    async def run_agent():
        try:
            await agent.ainvoke(lc_messages, callbacks=[handler])
        except Exception as e:
            await queue.put(f"data: [ERROR] {str(e)}\n\n")
        finally:
            await queue.put("data: [DONE]\n\n")

    asyncio.create_task(run_agent())

    async def event_stream():
        while True:
            msg = await queue.get()
            yield msg
            if msg.strip() == "data: [DONE]":
                break

    return event_stream()


def to_langchain_messages(messages: list[Message]) -> dict:
    """
    LangChain agent가 요구하는 {"input": str, "chat_history": list[BaseMessage]} 형태로 분리합니다.

    :param messages: 사용자 정의 Message 객체 리스트 (role: "user" | "assistant")
    :return: dict with "input" and "chat_history"
    """
    lc_messages: list[BaseMessage] = []
    for message in messages:
        if message.role == "user":
            lc_messages.append(HumanMessage(content=message.content))
        elif message.role == "assistant":
            lc_messages.append(AIMessage(content=message.content))

    if not lc_messages or not isinstance(lc_messages[-1], HumanMessage):
        raise ValueError("마지막 메시지는 사용자(HumanMessage)여야 합니다.")

    *chat_history, latest = lc_messages

    return {
        "input": latest.content,
        "chat_history": chat_history,
    }
