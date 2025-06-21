from typing import Annotated, Dict, List, Optional, TypedDict, Literal

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    user_query: Optional[str]
    messages: Annotated[list, add_messages]

    next_node: Optional[str]
    intent: Literal["tavel_conversation", "search"]

    travel_city: Optional[str]
    travel_place: Optional[List[str]]
    travel_schedule: Optional[str]
    travel_style: Optional[str]
    need_place_search: Optional[bool]

    travel_conversation_raw_output: Optional[str]
    travel_conversation_json_output: Optional[dict]

    travel_plan: Optional[dict]

    tavily_search_result: Optional[List[dict]]
    share_url: Optional[str]


def get_latest_messages(messages):
    latest_ai = ""
    latest_human = ""

    for message in reversed(messages):
        if not latest_ai and isinstance(message, AIMessage):
            latest_ai = message.content
        elif not latest_human and isinstance(message, HumanMessage):
            latest_human = message.content
        if latest_ai and latest_human:
            break

    return latest_ai, latest_human

def get_last_message(messages):
    return messages[-1].content if messages else ""