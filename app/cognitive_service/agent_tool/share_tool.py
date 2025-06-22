from langchain_core.messages import AIMessage, tool

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.logger.logger_config import api_logger


def travel_plan_action_conversation(state: AgentState):
    api_logger.info(
        f"[plan_share_action!!!] 현재 상태 정보입니다: {state.get("messages", [])}"
    )
    messages = state.get("messages", [])
    plan_intent = state.get("intent", "")
    travel_plan_markdown = state.get("travel_plan_markdown", "")

    response = ""
    if plan_intent != "plan_share":
        response = f"잘못된 노드를 호출했습니다. 일정 곌획 공유 일정 관리에 대한 의도가 아닙니다. 선택된 의도: {plan_intent}"
    elif plan_intent == "plan_share":
        if not travel_plan_markdown:
            response = f"추출된 마크다운이 없습니다. 공유할 여행 계획 정보가 없습니다."
        else:
            response = f"{travel_plan_markdown}을 파일로 저장하고 공유 가능한 URL을 전달합니다."
    else:
        response = f"{plan_intent}는 해당 에이전트에서 지워하지 않습니다."

    return {"messages": messages + [AIMessage(content=response)]}
