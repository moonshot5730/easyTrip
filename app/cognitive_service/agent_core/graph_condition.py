from typing import Literal

from langgraph.constants import END

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.logger.logger_config import api_logger


def lang_condition(branch: str) -> dict:
    return {"__return__": branch}


def should_conversation(state: AgentState) -> str:
    """
    :param state: 현재 그래프 상태 정보
    :return: 라우팅될 엣지 정보
    """
    extract_travel_info = all(
        [
            state.get("travel_schedule") not in [None, "", "미정"],
            state.get("travel_style") not in [None, "", "미정"],
        ]
    )

    if extract_travel_info:
        if state.get("travel_place") not in [None, "", "미정"]:
            return "complete"
        elif state.get("need_place_search") is True:
            return "search"
        else:
            return "loop"

    return "complete"


def supervisor_router_str(
    state: AgentState,
) -> Literal["conversation", "search", "complete"]:
    """
    체크포인트로 저장된 state 정보를 보고 분기:
    - travel_place, travel_schedule, travel_style이 모두 비어 있고 검색 요청도 없는 경우 → 대화 시작 및 여행 안내(loop)
    - style/schedule은 채워졌고,
        - 장소가 비어 있고 검색 요청 있음 → search
        - 장소까지 있으면 → complete [여행 계획 세워주기]
        - 장소가 없고 검색 요청도 없음 → loop
    - 그 외 → complete [대화 끝]
    """

    def is_blank(value):
        return value in (None, "", "미정")

    travel_place = state.get("travel_place")
    travel_schedule = state.get("travel_schedule")
    travel_style = state.get("travel_style")
    need_place_search = state.get("need_place_search")

    result = "conversation"
    if (
        all(map(is_blank, [travel_place, travel_schedule, travel_style]))
        and need_place_search is False
    ):
        result = "conversation"

    if not is_blank(travel_schedule) and not is_blank(travel_style):
        if is_blank(travel_place):
            result = "search" if need_place_search else "conversation"
        else:
            result = "complete"

    print(f" supervisor_router 반환 정보: {result} {type(result)}")
    print(f" 현재 state 정보 : {state} {type(result)}")

    return result


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
