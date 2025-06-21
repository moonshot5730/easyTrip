from langgraph.constants import END

from app.cognitive_service.agent_core.graph_state import AgentState


def should_go_to_router(state: AgentState) -> str:
    # 정보가 다 채워졌는지 확인
    required_fields = [
        state.get("want_travel_city"),
        state.get("travel_schedule"),
        state.get("travel_style"),
    ]
    # 최소 하나라도 비어 있으면 계속 대화
    if any(field is None for field in required_fields):
        return END  # 계속 대화
    return "intent_router"  # 이제 라우터로 이동


def should_conversation(state: AgentState) -> str:
    extract_travel_info = all([
        state.get("travel_schedule") not in [None, "", "미정"],
        state.get("travel_style") not in [None, "", "미정"]
    ])

    if extract_travel_info:
        if state.get("travel_place") not in [None, "", "미정"]:
            return "complete"
        elif state.get("need_place_search") is True:
            return "search"
        else:
            return "loop"

    return "complete"


def start_router(state: AgentState) -> str:
    """
    체크포인트로 복원된 state에 따라 분기
    """
    extract_travel_info = all([
        state.get("travel_schedule") not in [None, "", "미정"],
        state.get("travel_style") not in [None, "", "미정"]
    ])

    if extract_travel_info:
        if state.get("travel_place") not in [None, "", "미정"]:
            return "complete"
        elif state.get("need_place_search") is True:
            return "search"
        else:
            return "loop"

    return "complete"
