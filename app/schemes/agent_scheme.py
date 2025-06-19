from typing import TypedDict, Literal, List


class ChatMessage(TypedDict):
    role: Literal["user", "assistant", "tool"]
    content: str


class ChatRequest(TypedDict):
    session_id: str
    messages: List[ChatMessage]
