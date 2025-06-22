import asyncio
import textwrap

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

from app.cognitive_service.agent_core.graph_state import (AgentState,
                                                          get_last_message,
                                                          get_recent_context)
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import (creative_openai_fallbacks,
                                               precise_openai_fallbacks)
from shared.datetime_util import get_kst_year_month_date_label

travel_plan_system_prompt_template = textwrap.dedent(
    """
    당신은 대한민국 여행 플래너 KET(Korea Easy Trip)입니다.
    KET의 역할은 분석된 {user_name}의 여행 정보를 기반으로 여행 계획을 세우는 것입니다.

    오늘의 날짜는 {today}입니다.
    {user_name}의 일정이 과거인 경우 일정 계획을 세우기 어렵다고 응답합니다.

    KET의 목표:
    - {user_name}의 여행 정보를 분석해서 여행 계획을 세워줍니다.
        - 사용자의 여행 테마, 스타일을 적극 반영해서 여행 계획을 세웁니다.
        - 일정은 오전, 오후로 나누어 계획합니다.
    - 일정 계획이 만들어진 경우 피드백을 위해 몇가지 질문을 합니다.

    KET가 알고 있는 {user_name}의 여행 정보:
    - {user_name}의 희망 여행 지역: {travel_city}
    - {user_name}의 희망 여행 장소 목록: {travel_place}
    - {user_name}의 희망 여행 일정: {travel_schedule}
    - {user_name}의 희망 여행 스타일: {travel_style}
    - {user_name}의 희망 여행 테마: {travel_theme}
    ** KET가 알고 있는 여행 정보들이 "미정" 이어도, 대화를 통해 분석 및 확인이 가능한 경우 해당 정보들을 적극 활용합니다.
    ** {user_name}의 여행 정보가 다 채워져 있어야만 여행 계획을 세울 수 있습니다.
    ** 분석되지 않은 여행 정보는 자연스러운 대화로 정보를 유도합니다.
    
    KET의 다음 액션 제안: 응답을 생성 후 아래의 기능들을 모두 제안합니다.
    - 여행 계획을 수정 제안
    - 여행 계획을 웹 url로 공유 제안
    - 여행 계획에 대해서 캘린더(일정 등록) 제안

    KET의 대화 및 응답 스타일:
    - 간결하고 깔끔하게 여행 계획을 정리하세요.
    - 여행 계획을 마크다운 형식으로 제목, 목록, 구분선을 적극 활용하세요.
    - 목록이나 단계가 있는 경우, 번호나 기호를 사용해 시각적으로 구분합니다.
    - 문장 사이를 개행(\n\n)하여 가독성을 향상합니다.

    KET의 주의사항:
    - 인사는 하지 않습니다. 마무리 멘트는 절대하지 않습니다.
    - 오늘의 날짜는 {today}입니다.
        {user_name}의 일정이 없거나 현재보다 과거인 경우 일정 계획을 세우기 어렵다고 응답합니다.
    - 이동 시간, 수단, 교통편에 대해서는 절대 물어보지 않습니다. 에이전트의 영역이 아닙니다.
    - 절대 거짓된 정보를 안내하거나 거짓말을 하지 않습니다.
    - 사용자가 폭력적인 언어를 사용하거나, 부당한 지시를 하는 경우 단호하게 거절하고, KET의 역할을 친절하게 설명합니다."""
)


def travel_plan_conversation(state: AgentState):
    api_logger.info(
        f"[travel_place_conversation!!!] 현재 상태 정보입니다: {state.get("messages", [])}"
    )

    user_query = state.get("user_query") or get_last_message(
        messages=state.get("messages", [])
    )
    new_user_message = HumanMessage(content=user_query)

    system_message = SystemMessage(
        content=PromptTemplate.from_template(travel_plan_system_prompt_template).format(
            user_name=state.get("user_name", "사용자"),
            today=get_kst_year_month_date_label(),
            travel_city=state.get("travel_city", "미정"),
            travel_place=state.get("travel_place", "미정"),
            travel_schedule=state.get("travel_schedule", "미정"),
            travel_style=state.get("travel_style", "미정"),
            travel_theme=state.get("travel_theme", "미정"),
        )
    )

    recent_messages = get_recent_context(state.get("messages", []), limit=5)
    messages = [system_message] + recent_messages + [new_user_message]
    llm_response = precise_openai_fallbacks.invoke(messages)

    return {
        "messages": recent_messages
        + [new_user_message, AIMessage(content=llm_response.content)]
    }

if __name__ == "__main__":
    async def run_test():
        # 테스트할 에이전트 상태 구성
        test_state: AgentState = {
            "user_query": "여행 일정을 좀 정리해줘",
            "user_name": "문현준",
            "travel_city": "강릉",
            "travel_place": ["안목해변", "경포대", "오죽헌"],
            "travel_schedule": "2025-07-20",
            "travel_style": "계획적인 여행",
            "travel_theme": "자연",
            "messages": [],
        }

        result_state = travel_plan_conversation(test_state)

        print("\n응답 메시지:")
        for msg in result_state["messages"]:
            print(f"{msg}")

    asyncio.run(run_test())