from typing import Literal

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.logger.logger_config import api_logger


def state_router(state: AgentState) -> dict:
    api_logger.info(f" 현재 state 정보 : {state}")
    updated_state = state.copy()

    travel_plan_status = state.get("travel_plan_status", "")
    intent = state.get("intent")  # Literal["travel_conversation", "manage_calendar", "travel_plan", "plan_share", "aggressive_query"]

    match intent, travel_plan_status:
        case ("travel_conversation", _):
            next_node = "travel_conversation"
        case ("travel_plan", status) if status in ("update", ""):
            next_node = "travel_plan"
        case (intent, "complete") if intent in (
            "manage_calendar",
            "plan_share",
            "travel_plan",
        ):
            next_node = "plan_action"
        case ("aggressive_query", _):
            next_node = "aggressive_query"
        case _:
            next_node = "travel_conversation"

    updated_state["next_node"] = next_node

    api_logger.info(f" supervisor_router 반환 정보: {next_node}")
    api_logger.info(f" 갱신된 state 정보 : {updated_state}")
    return updated_state


def is_websearch(state: AgentState) -> str:
    api_logger.info(f"웹 검색을 수행하여 분기합니다. {state.get("is_websearh")}")
    return "web_summary" if state.get("is_websearh") else "extract"


def check_plan_action(state: AgentState) -> str:
    plan_intent = state.get("plan_intent", "")
    plan_action = state.get("plan_action", "")

    api_logger.info(f"여행 계획에 대한 요청 작업을  분기합니다. 의도 정보: {plan_intent}, 액션 정보: {plan_action}")
    return plan_intent
