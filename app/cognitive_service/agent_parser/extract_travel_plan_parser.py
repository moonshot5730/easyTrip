import textwrap
from typing import List, Literal, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from app.cognitive_service.agent_core.graph_state import (
    AgentState, get_last_human_message, get_last_message, get_recent_context)
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks
from shared.format_util import format_user_messages_with_index


class TravelPlanOutput(BaseModel):
    travel_plan_dict: Optional[dict] = Field(default={})
    travel_plan_markdown: Optional[str] = Field(default="")
    travel_plan_status: Optional[Literal["complete", "update"]] = Field(default="ready")
    intent: Optional[
        Literal["manage_calendar", "plan_share", "travel_plan", "aggressive_query"]
    ] = Field(default="travel_plan")


travel_plan_parser = PydanticOutputParser(pydantic_object=TravelPlanOutput)

extract_travel_plan_prompt = PromptTemplate.from_template(
    textwrap.dedent(
        """
        당신은 사용자와의 최근 대화를 분석해서 여행 계획 정보를 분석 및 추출하는 개체 추출기 KET야.
        KET는 대화에서 정리된 여행 계획 정보를 추출해서 정리 분석해

        KET가 추출할 개체 정보야:
        - travel_plan_dict: 여행 계획 일정에 대한 사전 자료 정보
            - key : 날짜 정보로 1일차, 2일차, 마지막 날 이렇게 정리
            - value: 여행 계획 정보 (텍스트),
        - travel_plan_markdown: 마크다운으로 정리된 여행 계획표
        - travel_plan_status: 대화에서 분석한 여행 계획의 상태 정보
            - 여행계획이 생성된 경우 complete, 없는 경우 update로 처리합니다.
        - intent: 마지막 사용자의 요청 정보를 분석해서 의도를 추출합니다.
            - manage_calendar: 여행 계획에 대해서 캘린더로 일정을 관리하고 싶은 경우
            - plan_share: 완성된 여행 계획을 파일로 공유하고 싶은 경우
            - travel_plan: 여행 계획을 수정하거나 개선 하고 싶은 경우
            - aggressive_query: 공격적이거나 폭력적인 표현을 사용한 경우
        ** 거짓된 정보, 모호한 정보는 추출하지 않습니다. 반드시 이해하고 분석한 정보 여행 계획을 추출합니다.

        응답 JSON 형식:
        {format_instructions}

        KET가 분석해야 할 대화:
        최근 대화 정보: {user_query}
        마지막 사용자 요청: {last_user_query}
        """
    )
).partial(format_instructions=travel_plan_parser.get_format_instructions())


def extract_travel_plan_llm_parser(state: AgentState):
    messages = state.get("messages", [])
    recent_messages = get_recent_context(messages, limit=4)

    formatted_prompt = extract_travel_plan_prompt.format(
        user_query=format_user_messages_with_index(recent_messages),
        last_user_query=get_last_human_message(messages),
    )
    llm_response = precise_openai_fallbacks.invoke(formatted_prompt)

    api_logger.info("[extract_travel_plan_llm_parser START!] 호출! ")

    travel_plan_info = travel_plan_parser.parse(llm_response.content)
    api_logger.info(travel_plan_info.model_dump_json(indent=2))

    return {
        "travel_plan_markdown": travel_plan_info.travel_plan_markdown,
        "travel_plan_dict": travel_plan_info.travel_plan_dict,
        "travel_plan_status": travel_plan_info.travel_plan_status,
        "intent": travel_plan_info.intent,
    }
