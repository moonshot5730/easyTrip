import textwrap

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

from app.cognitive_service.agent_core.graph_state import (AgentState,
                                                          get_last_message)
from app.cognitive_service.agent_llm.llm_models import creative_llm_nano
from shared.datetime_util import get_kst_year_month_date_label

travel_place_system_prompt_template = textwrap.dedent(
    """
    당신은 대한민국 여행 플래너 KET(Korea Easy Trip)입니다.
    KET의 목표는 {user_name}이 원하는 국내 여행지(지역, 장소)를 제안하고 추천하는 것입니다.
    {user_name}과의 대화를 분석하여 어울리는 여행 지역과 장소를 제안하고 추천합니다.
    오늘의 날짜는 {today}입니다.
    대한민국의 계절를 고민하여 추천 및 제안에 참고합니다.

    KET의 목표:
    - {user_name}의 여행 스타일을 분석합니다.
        - 자연, 문화, 음식, 놀거리 등등 어떤 유형의 여행을 선호하는지 질문
        - 계획적인 여행, 즉흥적인 여행 중 어떤 여행을 선호하는지 질문
    - 대화를 통해 여행 스타일을 확인할 수 있는 경우, {user_name}이 원하는 대한민국 여행지(지역, 도시)를 제안하고 추천합니다.

    KET의 대화 스타일:
    - 친절하고 자연스럽게 여행 지역 및 장소에 대해서 대화해
    - {user_name}에게 적합한 여행 지역 및 장소를 제안 및 추천해
    - 긴 문장의 경우 개행을 통해 가독성을 개선해. 필요한 경우 문단까지 구분해.
    ** 인사는 하지 않습니다.
    """
)


def travel_place_conversation(state: AgentState):
    print(
        f"[travel_place_conversation!!!] 현재 상태 정보이니다: {state.get("messages", [])}"
    )

    user_query = state.get("user_query") or get_last_message(
        messages=state.get("messages", [])
    )
    new_user_message = HumanMessage(content=user_query)

    system_message = SystemMessage(
        content=PromptTemplate.from_template(
            travel_place_system_prompt_template
        ).format(user_name="문현준", today=get_kst_year_month_date_label())
    )

    recent_messages = state.get("messages", [])[-4:]
    messages = [system_message] + recent_messages + [new_user_message]
    llm_response = creative_llm_nano.invoke(messages)

    return {
        "messages": state.get("messages", [])
        + [new_user_message, AIMessage(content=llm_response.content)]
    }
