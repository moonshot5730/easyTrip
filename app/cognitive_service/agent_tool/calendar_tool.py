from langchain_core.messages import AIMessage, tool

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.logger.logger_config import api_logger


def manage_calendar_action(state: AgentState):
    api_logger.info(
        f"[calendar_share_action!!!] 현재 상태 정보입니다: {state.get("messages", [])}"
    )
    messages = state.get("messages", [])
    intent = state.get("intent", "")
    plan_action = state.get("plan_action", "")

    response = ""
    if intent != "manage_calendar":
        response = f"잘못된 노드를 호출했습니다. 캘린더 일정 관리에 대한 의도가 아닙니다. 선택된 의도: {intent}"
    elif intent == "manage_calendar":
        if plan_action == "register_calendar":
            response = "캘린더에 일정을 등록합니다."
        elif plan_action == "read_calendar":
            response = "캘린더 일정을 조회합니다."
            # 여기에 조회 로직 추가
            response = "캘린더 일정을 삭제합니다."
        else:
            response = f"알 수 없는 캘린더 액션입니다: {plan_action}"
    else:
        response = f"지원하지 않는 의도입니다.: {intent}"

    return {"messages": messages + [AIMessage(content=response)]}
