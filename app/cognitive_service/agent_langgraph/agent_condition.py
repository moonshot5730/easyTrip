from langgraph.constants import END

from app.cognitive_service.agent_langgraph.agent_state import AgentState


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
