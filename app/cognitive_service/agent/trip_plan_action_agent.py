import textwrap
from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel

from app.cognitive_service.agent_core.graph_state import (AgentState,
                                                          get_last_message, get_last_human_message)
from app.cognitive_service.agent_tool.travel_search_tool import \
    place_search_tool
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks
from shared.datetime_util import get_kst_year_month_date_label

class PlanActionOutput(BaseModel):
    intent: Literal["plan_share", "manage_calendar"]
    action: Literal["register_calendar", "read_calendar", "update_calendar"]

plan_action_parser = PydanticOutputParser(pydantic_object=PlanActionOutput)

travel_plan_action_system_prompt_template = textwrap.dedent(
    """
    당신은 여행 계획 관련 사용자의 질의에서 의도를 분석하는 KET입니다.
    KET의 역할은 사용자의 요청 정보를 분석하고, 의도와 액션을 분류하는 것입니다.
    
    KET가 추출해야 할 의도와 액션 정보:
    - intent: 사용자의 요청의 의도 분류
        - plan_share: 여행 계획을 공유해달라는 요청, 공유가 핵심
        - manage_calendar: 여행 계획을 캘린더로 관리해달라는 요청
    - action: 사용자가 요청한 액션 정보
        - register_calendar : 일정 신규 등록을 요청한 경우
        - read_calendar : 등록된 일정이 있는지 조회
        - update_calendar: 기존 등록된 일정 수정 [삭제 후 추가]
        
    KET 응답 JSON 형식:
    {format_instructions}
        
     사용자 요청 정보: {user_query}""")


def travel_plan_action(state: AgentState):
    """
    :param state: 그래프 스테이트 정보
    :return: 연관된 tool 기능을 호출합니다.
    """
    api_logger.info(
        f"[travel_plan_action!!!] 현재 상태 정보입니다: {state.get("messages", [])}"
    )

    system_message = SystemMessage(
        content=PromptTemplate.from_template(
            travel_plan_action_system_prompt_template
        ).format(user_query=state.get("user_query", ""),
                 format_instructions=plan_action_parser.get_format_instructions()
         )
    )
    llm_response = precise_openai_fallbacks.invoke([system_message])
    plan_action_output = plan_action_parser.parse(llm_response.content)

    return {
        **state,
        "plan_intent": plan_action_output.intent,
        "plan_action": plan_action_output.action,
        "messages": state["messages"] + [AIMessage(content=plan_action_output.model_dump_json())],
    }
