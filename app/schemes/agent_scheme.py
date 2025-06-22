from typing import List, Literal, TypedDict


class ChatMessage(TypedDict):
    role: Literal["user", "assistant", "tool"]
    content: str


class ChatRequest(TypedDict):
    session_id: str
    user_name: str
    message: ChatMessage
