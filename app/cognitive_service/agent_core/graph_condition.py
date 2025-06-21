from typing import Literal

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.logger.logger_config import api_logger



def state_router(state: AgentState) -> dict:
    def is_blank(value):
        return value in (None, "", "미정")

    api_logger.info(f" 현재 state 정보 : {state}")
    updated_state = state.copy()

    travel_city = state.get("travel_city")
    travel_place = state.get("travel_place")
    travel_schedule = state.get("travel_schedule")
    travel_plan = state.get("travel_plan")

    match (
        is_blank(travel_city),
        is_blank(travel_place),
        is_blank(travel_schedule),
        is_blank(travel_plan),
    ):
        case (_, _, True, True):
            next_node = "travel_place_conversation"
        case (False, False, False, True):
            next_node = "travel_plan_conversation"
        case (False, False, False, False):
            next_node = "travel_plan_share"
        case _:
            next_node = "travel_place_conversation"

    updated_state["next_node"] = next_node

    api_logger.info(f" supervisor_router 반환 정보: {next_node}")
    api_logger.info(f" 갱신된 state 정보 : {updated_state}")
    return updated_state
