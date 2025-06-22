from typing import Annotated, Dict, List, Literal, Optional, TypedDict

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import add_messages


class AgentState(TypedDict):
    session_id: Optional[str]
    user_query: Optional[str]
    user_name: Optional[str]
    messages: Annotated[list, add_messages]

    next_node: Optional[str]
    intent: Literal[
        "travel_conversation",
        "manage_calendar",
        "travel_plan",
        "plan_share",
        "aggressive_query",
    ]
    plan_intent: Literal["manage_calendar", "plan_share", "plan_update"]
    plan_action: Literal[
        "register_calendar", "read_calendar", "update_calendar", "delete_calendar"
    ]

    travel_city: Optional[str]
    travel_place: Optional[List[str]]
    travel_schedule: Optional[str]
    travel_style: Optional[str]
    travel_theme: Optional[str]

    travel_plan_markdown: Optional[str]
    travel_plan_dict: Optional[dict]
    travel_plan_status: Optional[Literal["complete", "update"]]
    share_url: Optional[str]

    is_websearh: Optional[bool]
    websearch_results: Optional[str]


def get_recent_human_messages(messages, limit=8):
    return [
        message.content
        for message in reversed(messages[-limit:])
        if isinstance(message, HumanMessage)
    ]


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


def get_last_human_message(messages: list) -> str:
    for message in reversed(messages):
        if isinstance(message, HumanMessage):
            return message.content
    return ""


def get_recent_context(messages, limit=4):
    recent_messages = list(
        reversed(
            [
                message
                for message in reversed(messages)
                if not isinstance(message, SystemMessage)
            ][:limit]
        )
    )
    return recent_messages
