import json
import textwrap
from typing import Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from app.cognitive_service.agent_core.graph_state import (AgentState,
                                                          get_latest_messages)
from app.core.logger.logger_config import get_logger
from app.external.openai.openai_client import precise_llm_nano

logger = get_logger()


class TravelInfoOutput(BaseModel):
    travel_place: Optional[str] = Field(default="미정")
    travel_schedule: Optional[str] = Field(default="미정")
    travel_style: Optional[str] = Field(default="미정")
    need_place_search: Optional[bool] = Field(default="False")


travel_info_parser = PydanticOutputParser(pydantic_object=TravelInfoOutput)

extract_travel_info_prompt = PromptTemplate.from_template(
    textwrap.dedent(
        """
너는 최근 대화의 정보를 통해 사용자의 여행 장소, 여행 일정, 여행 스타일, 웹검색 필요 유무를 분석하는 KEA야.

KEA는 의도와 함께 대화에서 아래의 정보를 같이 추출해:
1. travel_place: 여행 도시 및 장소 정보
2. travel_schedule: 여행 스케줄 (YYYY-MM-DD)~(YYYY-MM-DD)
3. travel_style: 여행 스타일 정보
4. need_place_search: 웹 검색 필요 유무 

반드시 JSON으로 응답합니다. 
JSON 형식:
{format_instructions}

최근 AI 메시지: {ai_message}
사용자 메시지: {user_query}"""
    )
).partial(format_instructions=travel_info_parser.get_format_instructions())


def extract_info_llm_parser(state: AgentState):
    messages = state.get("messages", [])
    ai_message, user_query = get_latest_messages(messages)

    formatted_prompt = extract_travel_info_prompt.format(
        ai_message=ai_message, user_query=user_query
    )
    raw_output = precise_llm_nano.invoke(formatted_prompt)

    logger.info(
        f"[extract_info_llm_parser START!] 🧾 전송한 프롬프트 정보: {formatted_prompt}\n원본 LLM 응답:\n {raw_output.content}"
    )

    travel_info_output = travel_info_parser.parse(raw_output.content)
    logger.info(travel_info_output.model_dump_json(indent=2))

    return {
        "travel_place": travel_info_output.travel_place,
        "travel_schedule": travel_info_output.travel_schedule,
        "travel_style": travel_info_output.travel_style,
        "need_place_search": bool(travel_info_output.need_place_search),
    }
