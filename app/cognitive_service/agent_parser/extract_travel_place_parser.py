import textwrap
from typing import List, Optional, Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from app.cognitive_service.agent_core.graph_state import (AgentState,
                                                          get_recent_human_messages, get_latest_messages)
from app.cognitive_service.agent_llm.llm_models import precise_llm_nano
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks
from shared.datetime_util import get_kst_year_month_date_label
from shared.format_util import format_user_messages_with_index


class TravelPlaceOutput(BaseModel):
    travel_city: Optional[str] = Field(default="미정")
    travel_place: Optional[List[str]] = Field(default=["미정"])
    travel_schedule: Optional[str] = Field(default="미정")
    travel_style: Optional[str] = Field(default="미정")
    travel_theme: Optional[str] = Field(default="미정")
    intent: Optional[Literal["travel_conversation", "manage_calendar", "travel_plan", "plan_share", "aggressive_query"]] = Field(default="travel_conversation")

travel_place_parser = PydanticOutputParser(pydantic_object=TravelPlaceOutput)


extract_travel_info_prompt = PromptTemplate.from_template(
    textwrap.dedent(
        """
        당신은 사용자의 최근 응답들을 분석해서 여행 정보를 분석 및 추출하는 개체 추출기 KET야.
        KET는 사용자가 선호하는 여행 지역, 여행 장소, 여행 스타일, 여행 테마, 여행 일정 개체 정보를 추출해.
        
        KET가 추출할 개체 정보야:
        - travel_city: 여행 지역 및 도시
        - travel_place: 명확한 여행 장소 및 관광지 목록
        - travel_schedule: 계획중인 여행 일정 (YYYY-MM-DD~YYYY-MM-DD)
        - travel_style: 여행 계획 스타일 (즉흥, 계획, 상관없음 등등)
        - travel_theme: 계획중인 여행 테마 (자연, 힐링, 휴식, 놀거리 등등)
        - intent: 사용자가 요청한 가장 마지막 대화 정보: {last_user_query}의 의도 정보를 추출. 
            - travel_conversation: 최근, 유명한 곳, 등등에 대한 장소 추천 및 검색 요청
            - manage_calendar: 캘린더 기반의 일정 관리(수정, 등록, 삭제)를 요청
            - travel_plan: 여행 계획이 만들어진 경우, 여행 계획을 요청한 경우, 여행 계획을 만들어 달라고 요청 한 경우, 여행 계획이 필요한 경우
            - plan_share : 여행 계획을 공유해달라고 요청한 경우
            - aggressive_query: 공격적이거나 폭력적인 표현을 사용한 경우
        ** 거짓된 정보, 모호한 정보는 추출하지 않습니다. 반드시 사용자의 메시지 목록에서 추출합니다.
        
        KET의 주의사항:
        - 오늘의 날짜는 {today}야.
        - 날짜를 기준으로 여행 일정 정보를 추출해야해. [절대 과거 일정으로 추출하지 않습니다.] 
        - travel_place는 사용자가 명확하게 응답한 관광지와 여행 장소만 추출합니다.
        - travel_city의 경우 유추가 가능한 경우 지역명 혹은 도시명을 추출합니다.
        
        KET가 분석해야 할 대화:
        사용자 메시지 목록: {user_query}
        마지막 사용자의 요청 정보: {last_user_query}
        
        응답 JSON 형식:
        {format_instructions}
        """)).partial(format_instructions=travel_place_parser.get_format_instructions(), today=get_kst_year_month_date_label(),)



def extract_travel_place_llm_parser(state: AgentState):
    messages = state.get("messages", [])
    recent_human_messages = get_recent_human_messages(messages, limit=6)
    last_message = recent_human_messages[-1]

    formatted_prompt = extract_travel_info_prompt.format(
        user_query=format_user_messages_with_index(recent_human_messages),
        last_user_query=last_message
    )
    llm_response = precise_openai_fallbacks.invoke(formatted_prompt)

    api_logger.info(
        f"[extract_travel_place_llm_parser START!] 🧾 전송한 프롬프트 정보: {formatted_prompt}\n원본 LLM 응답:\n {llm_response.content}"
    )

    travel_place_info = travel_place_parser.parse(llm_response.content)
    api_logger.info(travel_place_info.model_dump_json(indent=2))

    new_style = travel_place_info.travel_style
    new_theme = travel_place_info.travel_theme
    current_style = state.get("travel_place", "")
    current_theme = state.get("travel_place", "")

    return {
        "travel_city": travel_place_info.travel_city,
        "travel_place": travel_place_info.travel_place,
        "travel_schedule": travel_place_info.travel_schedule,
        "travel_style": new_style if new_style not in (None, "") else current_style,
        "travel_theme": new_theme if new_theme not in (None, "") else current_theme,
        "intent": travel_place_info.intent
    }
