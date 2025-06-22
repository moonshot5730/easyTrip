import textwrap
from typing import Optional, Literal, List

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from app.cognitive_service.agent_core.graph_state import AgentState, get_recent_context
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks
from shared.format_util import format_user_messages_with_index


class TravelPlanOutput(BaseModel):
    travel_plan_dict: Optional[dict] = Field(default={})
    travel_plan_markdown: Optional[str] = Field(default="")
    travel_plan_status: Optional[Literal["complete", "progress", "feedback", "ready", "need_info"]] = Field(default="ready")
    travel_plan_feedback: Optional[str] = Field(default="")

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
        - travel_plan_feedback: 더 좋은 여행 계획을 위한 KET의 피드백
        ** 거짓된 정보, 모호한 정보는 추출하지 않습니다. 반드시 이해하고 분석한 정보 여행 계획을 추출합니다.

        KET의 주의사항:
        - 사용자가 명확하게 여행 계획을 요청하지 않은 경우, 혹은 여행 계획을 세우기에 정보가 부족한 경우 travel_plan_status를 need_info로 설정합니다.
        - need_info인 경우 travel_plan_feedback에 어떤 정보들이 필요한지를 보완해서 제안합니다.

        응답 JSON 형식:
        {format_instructions}

        KET가 분석해야 할 대화:
        최근 대화 정보: {user_query}""")).partial(format_instructions=travel_plan_parser.get_format_instructions())


def extract_travel_plan_llm_parser(state: AgentState):
    messages = state.get("messages", [])
    recent_messages = get_recent_context(messages, limit=4)

    formatted_prompt = extract_travel_plan_prompt.format(
        user_query=format_user_messages_with_index(recent_messages)
    )
    llm_response = precise_openai_fallbacks.invoke(formatted_prompt)

    api_logger.info(
        f"[extract_travel_plan_llm_parser START!] 🧾 전송한 프롬프트 정보: {formatted_prompt}\n원본 LLM 응답:\n {llm_response.content}"
    )

    travel_plan_info = travel_plan_parser.parse(llm_response.content)
    api_logger.info(travel_plan_info.model_dump_json(indent=2))

    return {
        "travel_plan_markdown": travel_plan_info.travel_plan_markdown,
        "travel_plan_dict": travel_plan_info.travel_plan_dict,
        "travel_plan_status": travel_plan_info.travel_plan_status,
        "travel_plan_feedback" : travel_plan_info.travel_plan_feedback,
    }