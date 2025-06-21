import textwrap

from langchain_core.messages import AIMessage
from langchain_core.prompts import PromptTemplate

from app.cognitive_service.agent_core.graph_state import (AgentState,
                                                          get_last_message)
from app.external.openai.openai_client import creative_llm_nano, creative_openai_fallbacks
from shared.datetime_util import get_kst_year_month_date_label


def travel_conversation(state: AgentState):
    user_query = get_last_message(messages=state["messages"])

    travel_conversation_prompt = PromptTemplate.from_template(
        textwrap.dedent(
            """
    너는 {user_name}과의 대화를 통해 여행 스타일, 일정, 장소를 분석해주는 대한민국 개인 여행 플래너 KET야.
    KET의 목표는 대한민국의 다양한 지역과 도시 여행을 계획해주는 거야..
    KET는 여행 계획을 세울 준비를 하는 {user_name}과 자연스러운 대화를 하면서 여행 계획에 필요한 정보를 분석 정리해.
    오늘의 날짜는 {today}야. 
    
    {user_name}의 여행 정보:
    - travel_place (여행 장소): {travel_place} 
    - travel_schedule (여행 일정): {travel_schedule}
    - travel_style (여행 스타일): {travel_style}
    - need_place_search (여행 장소 검색 요청): {need_place_search}
    ** 분석되지 않은 여행 정보는 자연스러운 대화로 정보를 유도합니다.
    
    KET의 스타일:
    - {user_name}의 여행 계획을 위해 일정, 스타일, 장소와 관련된 대화해.
    - 대화 도중에 {user_name}의 이름을 언급하면서 자연스럽고 친근하게 대화해.
    - 가독성 있게 응답해. 필요한 경우 적절하게 마크다운을 사용하고 문장을 구분해줘.
    
    KET는 여행 계획을 위해 {user_name}의 여행 정보들을 친절하게 물어보고 유도합니다.
    - 여행 스타일 : 어떤 여행 스타일을 원하시나요? 문화, 자연, 휴식, 힐링, 음식 등등
    - 여행 장소 : 어떤 지역을 여행하고 싶은가요?, 계획한 장소가 있을까요?
    - 여행 일정 : 계획한 여행 일정이 있을까요?
    ** 고민되거나, 필요한 경우 여행 장소를 위한 웹 검색을 지원해줄 수 있다고 안내합니다.
    
    사용자 메시지: {user_query}"""
        )
    ).partial(user_name=state.get("user_name", "사용자"), today=get_kst_year_month_date_label())

    formatted_prompt = travel_conversation_prompt.format(
        travel_place=state.get("travel_place", "미정"),
        travel_schedule=state.get("travel_schedule", "미정"),
        travel_style=state.get("travel_place", "미정"),
        user_query=user_query,
    )

    llm_response = creative_openai_fallbacks.invoke(formatted_prompt)
    print(
        f"🧾 전송한 프롬프트 정보: {formatted_prompt}\n원본 LLM 응답:\n {llm_response.content}"
    )
    return {
        "messages": [AIMessage(content=llm_response.content)],
        "travel_conversation_raw_output": llm_response.content,
    }
