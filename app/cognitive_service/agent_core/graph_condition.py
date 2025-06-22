from typing import Literal

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.logger.logger_config import api_logger



def state_router(state: AgentState) -> dict:
    # def is_blank(value):
    #     return value in (None, "", "미정")
    #
    # def is_blank_list(value):
    #     return not value or value == ["미정"] or value == [""]

    api_logger.info(f" 현재 state 정보 : {state}")
    updated_state = state.copy()

    # travel_city = state.get("travel_city")
    # travel_place = state.get("travel_place")
    # travel_schedule = state.get("travel_schedule")
    # travel_plan = state.get("travel_plan")
    intent = state.get("intent") # Literal["travel_conversation", "manage_calendar", "travel_plan", "plan_share"]

    match (
        intent
    ):
        case "travel_conversation":
            next_node = "travel_conversation"
        case "manage_calendar":
            next_node = "travel_schedule"
        case "travel_plan":
            next_node = "travel_plan"
        case "plan_share":
            next_node = "plan_share"
        case _:
            next_node = "travel_conversation"

    updated_state["next_node"] = next_node

    api_logger.info(f" supervisor_router 반환 정보: {next_node}")
    api_logger.info(f" 갱신된 state 정보 : {updated_state}")
    return updated_state


def is_websearch(state: AgentState) -> str:
    api_logger.info(f"웹 검색을 수행하여 분기합니다. {state.get("is_websearh")}")
    return "web_summary" if state.get("is_websearh") else "extract"