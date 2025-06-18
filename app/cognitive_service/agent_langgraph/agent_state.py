from typing import TypedDict, List, Optional, Annotated, Dict, Literal

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    action: Optional[str]
    keywords: Optional[List[str]]
    want_travel_city: Optional[str]
    travel_schedule: Optional[str]
    search_results: List[Dict[str, str]]


class ChatMessage(TypedDict):
    role: Literal["user", "assistant", "tool"]
    content: str


class ChatRequest(TypedDict):
    messages: List[ChatMessage]


