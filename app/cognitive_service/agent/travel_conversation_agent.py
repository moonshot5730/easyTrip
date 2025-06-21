import textwrap

from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate

from app.cognitive_service.agent_core.graph_state import AgentState
from app.external.openai.openai_client import precise_llm_nano, creative_llm_nano
from shared.datetime_util import get_kst_timestamp_label, get_kst_year_month_date_label


def travel_conversation(state: AgentState):
    user_query = state["messages"][-1].content if state["messages"] else ""

    travel_conversation_prompt = PromptTemplate.from_template(textwrap.dedent("""
    너는 문현준과의 대화를 통해 여행 스타일, 일정, 장소를 분석해주는 대한민국 여행 컨설턴트 KET야.
    KET는 대한민국의 다양한 지역과 도시를 소개해.
    KET는 국내 여행 계획을 세울 준비를 하는 문현준과 대화하면서 여행 계획에 필요한 정보를 분석 정리해.
    오늘의 날짜는 {today}야. 
    
    사용자 문현준의 여행 정보:
    - travel_place (여행 장소): {travel_place} 
    - travel_schedule (여행 일정): {travel_schedule}
    - travel_style (여행 스타일): {travel_style}
    - need_place_search (여행 장소 검색 요청): {need_place_search}
    ** 미정인 경우 대화로 자엽스럽게 물어봅니다.
    
    KET의 목적:
    문현준의 여행 정보를 위해 일정, 스타일, 장소를 자연스럽게 물어보고, 필요하다는 요청을 합니다.
    KET는 사용자의 이름을 자주 언급하면서 친절하게 접근합니다.
    
    KET는 문현준을 위한 여행 정보를 위한 질문을 합니다:
    여행 계획을 위해 문현준의 여행 정보들을 친절하게 물어보고 유도합니다.
    - 여행 스타일 : 어떤 여행 스타일을 원하시나요? 문화, 자연, 휴식, 힐링, 음식 등등
    - 여행 장소 : 어떤 지역을 여행하고 싶은가요?, 계획한 장소가 있을까요?
    - 여행 일정 : 계획한 여행 일정이 있을까요?
    ** 필요한 경우 여행 장소를 위한 웹 검색을 지원해줄 수 있다고 안내합니다.

    
    사용자 메시지: {user_query}""")).partial(today=get_kst_year_month_date_label())

    formatted_prompt = travel_conversation_prompt.format(
        travel_place=state.get("travel_place", "미정"),
        travel_schedule=state.get("travel_schedule", "미정"),
        travel_style=state.get("travel_place", "미정"),
        need_place_search=state.get("need_place_search", "true"),
        user_query=user_query,
    )

    llm_response = creative_llm_nano.invoke(formatted_prompt)
    print(f"🧾 전송한 프롬프트 정보: {formatted_prompt}\n원본 LLM 응답:\n {llm_response.content}")
    return {"travel_conversation_raw_output": llm_response}


# 예시 메시지
messages = [
    HumanMessage(content="어디로 여행갈지 아직 정하지 못했어요."),
]

test_state = {
    "messages": messages,
    "travel_place": "미정",
    "travel_schedule": "미정",
    "travel_style": "미정",
    "need_place_search": "false",
}

result = travel_conversation(test_state)
print("🧪 travel_conversation 결과:\n", result["travel_conversation_raw_output"])