import textwrap
from typing import List, Literal, Optional

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field

from app.cognitive_service.agent_core.graph_state import (
    AgentState, get_last_message, get_recent_context,
    get_recent_human_messages)
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks
from shared.format_util import format_user_messages_with_index


class TravelPlanActionOutput(BaseModel):
    plan_intent: Optional[Literal["plan_share", "manage_calendar", "travel_plan"]] = (
        Field(default="travel_plan")
    )
    plan_action: Optional[
        Literal["register_calendar", "read_calendar", "update_calendar"]
    ] = Field(default="read_calendar")


travel_plan_action_parser = PydanticOutputParser(pydantic_object=TravelPlanActionOutput)

extract_travel_action_prompt = PromptTemplate.from_template(
    textwrap.dedent(
        """
        당신은 사용자의 최신 요청 정보에서 의도와 액션 정보를 분석하고 추출하는 개체 추출기 KET야.

        KET가 추출할 개체 정보야:
        - intent: 사용자의 요청의 의도 분류
            - plan_share: 여행 계획을 공유해달라는 요청, 공유가 핵심
            - manage_calendar: 여행 계획을 캘린더로 관리해달라는 요청
            - travel_plan: 계획에 대해서 수정하거나 보완해달라는 요청
        - action: 사용자가 요청한 액션 정보
            - register_calendar : 일정 신규 등록을 요청한 경우
            - read_calendar : 등록된 일정이 있는지 조회
            - update_calendar: 기존 등록된 일정 수정 [삭제 후 추가]
        ** 거짓된 정보, 모호한 정보는 추출하지 않습니다. 반드시 이해하고 분석한 의도와 액션 정보만 추출합니다.

        응답 JSON 형식:
        {format_instructions}

        KET가 분석해야 할 대화:
        최근 대화 정보: {user_query}
        마지막 사용자 요청: {last_user_query}
        """
    )
).partial(format_instructions=travel_plan_action_parser.get_format_instructions())


def extract_travel_plan_action_llm_parser(state: AgentState):
    api_logger.info(
        f"[extract_travel_plan_action_llm_parser START!] 🧾 계획 분기를 수행합니다!"
    )
    messages = state.get("messages", [])
    recent_messages = get_recent_human_messages(messages, limit=2)

    formatted_prompt = extract_travel_action_prompt.format(
        user_query=format_user_messages_with_index(recent_messages),
        last_user_query=get_last_message(messages),
    )
    llm_response = precise_openai_fallbacks.invoke(formatted_prompt)

    api_logger.info(
        f"[extract_travel_plan_action_llm_parser START!] 🧾 전송한 프롬프트 정보: {formatted_prompt}\n원본 LLM 응답:\n {llm_response.content}"
    )

    travel_plan_action_info = travel_plan_action_parser.parse(llm_response.content)
    api_logger.info(travel_plan_action_info.model_dump_json(indent=2))

    return {
        "intent": travel_plan_action_info.plan_intent,
        "plan_action": travel_plan_action_info.plan_action,
    }
