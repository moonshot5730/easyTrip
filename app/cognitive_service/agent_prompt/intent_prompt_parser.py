from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import Runnable, RunnableLambda, RunnableMap
from pydantic import BaseModel

from app.cognitive_service.agent_langgraph.agent_state import AgentState
from app.cognitive_service.agent_llm.llm_models import creative_openai_mini


class IntentOutput(BaseModel):
    action: Literal["search_travel_info", "create_travel_plan", "manage_travel_calendar", "share_travel_plan", "travel_conversation"]
    keywords: str


intent_parser = PydanticOutputParser(pydantic_object=IntentOutput)

intent_prompt_template = PromptTemplate.from_template("""
너의 이름은 KET야. KET는 여행 계획과 관련된 사용자의 요청을 분석해서 의도를 파악해. 
사용자의 요청에 따라 아래의 액션 중 **하나만 선택** JSON 형식으로 응답해.

가능한 액션 (반드시 아래 중 하나만 선택):
- search_travel_info (여행 장소 검색)  
  "어디로 가면 좋을까?", "추천해줘", "여행지 알려줘"와 같이 여행지를 탐색하거나 제안받고자 할 때 선택.  
  EX: "전주 여행지 추천해줘", "부산 여행지 알려줘"

- create_travel_plan (여행 계획 세우기)  
  여행 일정을 계획해달라고 요청할 때 선택.
  EX: "2박 3일 일정을 계획해줘", "하루 코스로 일정을 정리해줘", "동선을 고려해서 여행 계획 세워줘"

- manage_travel_calendar (여행 캘린더 일정 관리)  
  여행 일정을 캘린더에 관리할 때 선택.  
  EX: "계획 캘린더에 등록해줘", "등록한 일정 보여줘", "일정 삭제해줘"

- share_travel_plan (여행 계획 공유)  
  완성된 여행 계획을 다른 사람과 공유하고자 할 때 선택.
  EX: "이 계획 친구한테 보내줘", "공유 링크 만들어줘", "공유하고 싶어"

- travel_conversation (여행과 관련된 대화)
  일정, 여행지, 여행 스타일, 교통 수단 등등 여행과 관련된 대화를 진행할 때.  

JSON 형식:
{format_instructions}

사용자 입력:
{input}

주의사항:
- 반드시 1개의 액션만 선택할 것
- 액션과 관련된 가장 핵심이 되는 키워드 목록을 `keywords` 필드에 리스트 형태로 포함할 것
- 출력은 **JSON만**, 설명이나 주석은 포함하지 말 것
""")

# `format_instructions`를 삽입하여 모델이 응답 형식 맞추도록 유도
intent_prompt_template = intent_prompt_template.partial(format_instructions=intent_parser.get_format_instructions())

def extract_intent_as_action(state: AgentState) -> str:
    # 지정된 action이 없거나 유효하지 않으면 fallback
    valid_actions = {
        "search_travel_info",
        "create_travel_plan",
        "manage_travel_calendar",
        "share_travel_plan",
        "travel_conversation"
    }

    action = state.get("action", "travel_conversation")
    return action if action in valid_actions else "travel_conversation"

travel_advisor_prompt = ChatPromptTemplate.from_messages([
    ("system",
     "당신은 여행 계획을 도와주는 친절한 여행 컨설턴트입니다. "
     "사용자의 여행 목적, 장소, 일정, 스타일을 자연스럽게 대화하며 파악하세요. "
     "지나치게 질문하지 말고, 부드럽고 일상적인 대화처럼 이어가세요."),
    ("human", "{input}")
])

extract_user_input: Runnable = RunnableLambda(
    lambda state: {"input": next(
        (message.content for message in reversed(state["messages"]) if message.type == "human"),
        ""
    )}
)

# 4. 응답을 state에 다시 추가하는 후처리 노드
update_state_with_response: Runnable = RunnableLambda(
    lambda input: {
        **input,
        "messages": input["messages"] + [input["response"]]
    }
)

travel_conversation: Runnable = (
    {
        "input": extract_user_input,
        "messages": lambda state: state["messages"]  # 그대로 넘겨줌
    }
    | RunnableMap({
        "response": travel_advisor_prompt | creative_openai_mini,
        "messages": lambda d: d["messages"]
    })
    | update_state_with_response
)