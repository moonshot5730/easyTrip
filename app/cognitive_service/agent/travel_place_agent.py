import asyncio
import textwrap

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate

from app.cognitive_service.agent_core.graph_state import (
    AgentState, get_last_human_message, get_last_message, get_recent_context)
from app.cognitive_service.agent_tool.travel_search_tool import (
    get_web_search_results, place_search_tool)
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import creative_openai_fallbacks
from shared.datetime_util import get_kst_year_month_date_label

travel_place_system_prompt_template = textwrap.dedent(
    """
    당신은 대한민국 여행 플래너 KET(Korea Easy Trip)입니다.
    KET의 역할은 {user_name}의 여행 스타일을 분석하고, 어울리는 국내 여행지(지역, 장소)를 제안하고 추천하는 것입니다.
    {user_name}이 검색을 요청하는 경우 검색 도구를 사용합니다.
    
    오늘의 날짜는 {today}입니다.
    대한민국의 계절를 고민하여 추천 및 제안에 참고합니다.

    KET의 목표:
    - {user_name}의 여행 스타일 및 테마를 분석합니다.
        - 자연, 문화, 음식, 놀거리 등등 어떤 유형의 테마를 선호하는지 질문
        - 계획적인 여행, 즉흥적인 여행 중 어떤 스타일을 선호하는지 질문
        - 여행 일정은 어느정도로 계획하고 있는지 질문
    - 대화를 통해 {user_name}의 여행 스타일을 유추할 수 있는 경우 관련된 대한민국 여행지(지역, 장소)를 추천합니다.
    
    KET가 알고 있는 {user_name}의 여행 정보:
    - {user_name}의 희망 여행 지역: {travel_city}
    - {user_name}의 희망 여행 장소 목록: {travel_place}
    - {user_name}의 희망 여행 일정: {travel_schedule}
    - {user_name}의 희망 여행 스타일: {travel_style}
    - {user_name}의 희망 여행 테마: {travel_theme}
    ** KET가 알고 있는 여행 정보들이 "미정" 이어도, 사용자의 요청 정보에서 분석 및 확인이 가능한 경우 해당 정보를 적극 활용합니다.
    ** 분석되지 않은 여행 정보는 자연스러운 대화로 정보를 유도합니다.
    ** 희망 여행 지역, 장소 목록이 채워진 경우 여행 일정이나 계획을 세울 수 있는 다음 단계로 안내합니다.
    
    KET의 도구 사용 규칙:
    - {user_name}이 검색을 요청한 경우 웹 검색 도구 'tavily_web_search'을 사용합니다.
        - 질문에서 적절한 검색어를 추출하여 도구를 호출합니다.
        - 검색해, 최근, 요즘 등의 시점과 검색 요청이 핵심 트리거입니다.
    - {user_name}이 단순하게 여행 지역 및 장소를 추천 혹은 제안해 달라고 요청한 경우 관련된 여행 지역과 장소를 제안합니다.
        - 실시간 정보나 검색 요청이 아닌 경우 모델의 지식으로 응답합니다.
        - 여행 스타일, 테마, 계절 등의 기준으로 추천 및 정보를 요청할 때 
      
    사용 가능한 도구:
    - tavily_web_search: 질의에서 여행 키워드를 추출해 검색을 수행합니다.

    KET의 대화 및 응답 스타일:
    - 친절하고 자연스럽게 여행에 대해서 대화해.
    - 필요한 경우 마크다운 형식으로 제목, 목록, 구분선을 적극 활용하세요.
    - 목록이나 단계가 있는 경우, 번호나 기호를 사용해 시각적으로 구분합니다.
    - 문장 사이를 개행(\n\n)하여 가독성을 향상합니다.
    
    KET의 주의사항:
    - 인사는 하지 않습니다. 마무리 멘트는 절대하지 않습니다.
    - 항상 열린 질문이나 다음 행동을 유도하는 문장으로 끝맺습니다.
    - 절대 거짓된 정보를 안내하거나 거짓말을 하지 않습니다.
    - 사용자가 폭력적인 언어를 사용하거나, 부당한 지시를 하는 경우 단호하게 거절하고, KET의 역할을 친절하게 설명합니다."""
)


def travel_place_conversation(state: AgentState):
    messages = state.get("messages", [])
    api_logger.info(f"[travel_place_conversation!!!] 현재 상태 정보입니다: {messages}")

    user_query = state.get("user_query") or get_last_human_message(messages=messages)
    new_user_message = HumanMessage(content=user_query)

    system_message = SystemMessage(
        content=PromptTemplate.from_template(
            travel_place_system_prompt_template
        ).format(
            user_name=state.get("user_name", "사용자"),
            today=get_kst_year_month_date_label(),
            travel_city=state.get("travel_city", "미정"),
            travel_place=state.get("travel_place", "미정"),
            travel_schedule=state.get("travel_schedule", "미정"),
            travel_style=state.get("travel_style", "미정"),
            travel_theme=state.get("travel_theme", "미정"),
        )
    )

    recent_messages = get_recent_context(state.get("messages", []), limit=4)
    new_messages = [system_message] + recent_messages + [new_user_message]
    llm_response = creative_openai_fallbacks.bind_tools([place_search_tool]).invoke(
        new_messages
    )

    tool_messages = get_web_search_results(llm_response)
    websearch_results = "\n\n".join(msg.content for msg in tool_messages)

    return {
        "messages": recent_messages
        + [new_user_message, AIMessage(content=llm_response.content)]
        + tool_messages,
        "is_websearh": True if tool_messages else False,
        "websearch_results": websearch_results,
    }


# 테스트용 main 진입
if __name__ == "__main__":
    async def run_test():
        test_search_state: AgentState = {
            "user_query": "요즘 갈만한 국내 여행지 추천 및 검색해줘",
            "user_name": "문현준",
            "travel_city": "미정",
            "travel_place": "미정",
            "travel_schedule": "미정",
            "travel_style": "계획적인 여행",
            "travel_theme": "자연",
            "messages": [],
        }

        test_state: AgentState = {
            "user_query": "2박 3일 일정으로 국내 여행을 계획하고 있어",
            "user_name": "문현준",
            "travel_city": "미정",
            "travel_place": "미정",
            "travel_schedule": "미정",
            "travel_style": "계획적인 여행",
            "travel_theme": "자연",
            "messages": [],
        }

        result_search_state = travel_place_conversation(test_search_state)
        result_state = travel_place_conversation(test_state)

        print("\n[search 호출 테스트] 웹검색을 수행해야 함")
        print("\n🔎웹검색 수행 여부:", result_search_state.get("is_websearh"))
        print("\n🌐 웹 검색 결과 요약:\n", result_search_state.get("websearch_results"))

        print("\n[search 호출 테스트] 웹 검색 없이 일반 응답 제공해야 함")
        print("\n🔎 웹검색 수행 여부:", result_state.get("is_websearh"))
        print("\n🌐 웹 검색 결과 요약:\n", result_state.get("websearch_results"))

    asyncio.run(run_test())