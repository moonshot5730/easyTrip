import textwrap
from typing import List, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from app.cognitive_service.agent_core.graph_state import (AgentState,
                                                          get_latest_messages, get_recent_human_messages)
from app.cognitive_service.agent_llm.llm_models import precise_llm_nano
from app.core.logger.logger_config import api_logger
from shared.format_util import format_user_messages_with_index


class TravelPlaceOutput(BaseModel):
    travel_city: Optional[str] = Field(default="미정")
    travel_place: Optional[List[str]] = Field(default=["미정"])

travel_place_parser = PydanticOutputParser(pydantic_object=TravelPlaceOutput)

extract_travel_info_prompt = PromptTemplate.from_template(
    textwrap.dedent(
        """
        당신은 사용자의 최근 대화를 분석해서 여행을 위한 주요 정보를 추출하는 개체 추출기 KET야.
        KET는 최근 사용자의 요청 메시지 목록을 분석해서 사용자가 선호하는 여행 지역, 여행 장소 개체 정보를 추출해.
        
        KET가 추출할 개체 정보야:
        - travel_city: 여행 지역 및 도시
        - travel_place: 세부 여행 장소 목록
        ** 거짓된 정보, 모호한 정보는 추출하지 않습니다.
        
        응답 JSON 형식:
        {format_instructions}
        
        KET가 분석해야 할 대화:
        사용자 메시지 목록: {user_query}""")).partial(format_instructions=travel_place_parser.get_format_instructions())


def extract_travel_place_llm_parser(state: AgentState):
    messages = state.get("messages", [])
    recent_human_messages = get_recent_human_messages(messages)

    formatted_prompt = extract_travel_info_prompt.format(
        user_query=format_user_messages_with_index(recent_human_messages)
    )
    llm_response = precise_llm_nano.invoke(formatted_prompt)

    api_logger.info(
        f"[extract_travel_place_llm_parser START!] 🧾 전송한 프롬프트 정보: {formatted_prompt}\n원본 LLM 응답:\n {llm_response.content}"
    )

    travel_place_info = travel_place_parser.parse(llm_response.content)
    api_logger.info(travel_place_info.model_dump_json(indent=2))

    return {
        "travel_city": travel_place_info.travel_city,
        "travel_place": travel_place_info.travel_place,
    }
