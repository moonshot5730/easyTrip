import textwrap
from pprint import pprint

from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langgraph.constants import END
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode

from app.cognitive_service.agent_core.graph_state import AgentState
from app.cognitive_service.agent_parser.llm_json_parser import extract_info_llm_parser
from app.cognitive_service.agent_tool.extract_json_tool import extract_travel_info
from app.cognitive_service.agent_tool.travel_search_tool import search_place_tool
from app.external.openai.openai_client import precise_llm_nano, creative_llm_nano
from shared.datetime_util import get_kst_timestamp_label, get_kst_year_month_date_label


def travel_conversation(state: AgentState):
    user_query = state["messages"][-1].content if state["messages"] else ""

    travel_conversation_prompt = PromptTemplate.from_template(textwrap.dedent("""
    너는 {user_name}과의 대화를 통해 여행 스타일, 일정, 장소를 분석해주는 대한민국 여행 컨설턴트 KET야.
    KET는 대한민국의 다양한 지역과 도시를 소개해.
    KET는 국내 여행 계획을 세울 준비를 하는 {user_name}과 대화하면서 여행 계획에 필요한 정보를 분석 정리해.
    오늘의 날짜는 {today}야. 
    
    사용자 {user_name}의 여행 정보:
    - travel_place (여행 장소): {travel_place} 
    - travel_schedule (여행 일정): {travel_schedule}
    - travel_style (여행 스타일): {travel_style}
    - need_place_search (여행 장소 검색 요청): {need_place_search}
    ** 미정인 경우 대화로 자엽스럽게 물어봅니다.
    
    KET의 목적:
    {user_name}의 여행 정보를 위해 일정, 스타일, 장소를 자연스럽게 물어보고, 필요하다는 요청을 합니다.
    KET는 사용자의 이름을 자주 언급하면서 친절하게 접근합니다.
    
    KET는 {user_name}을 위한 여행 정보를 위한 질문을 합니다:
    여행 계획을 위해 {user_name}의 여행 정보들을 친절하게 물어보고 유도합니다.
    - 여행 스타일 : 어떤 여행 스타일을 원하시나요? 문화, 자연, 휴식, 힐링, 음식 등등
    - 여행 장소 : 어떤 지역을 여행하고 싶은가요?, 계획한 장소가 있을까요?
    - 여행 일정 : 계획한 여행 일정이 있을까요?
    ** 필요한 경우 여행 장소를 위한 웹 검색을 지원해줄 수 있다고 안내합니다.

    
    사용자 메시지: {user_query}""")).partial(user_name="문현준", today=get_kst_year_month_date_label())

    formatted_prompt = travel_conversation_prompt.format(
        travel_place=state.get("travel_place", "미정"),
        travel_schedule=state.get("travel_schedule", "미정"),
        travel_style=state.get("travel_place", "미정"),
        need_place_search=state.get("need_place_search", "false"),
        user_query=user_query,
    )

    llm_response = creative_llm_nano.invoke(formatted_prompt)
    print(f"🧾 전송한 프롬프트 정보: {formatted_prompt}\n원본 LLM 응답:\n {llm_response.content}")
    return {
        "messages": [AIMessage(content=llm_response.content)],
        "travel_conversation_raw_output": llm_response
    }


def should_conversation(state: AgentState) -> str:
    extract_travel_info = all([
        state.get("travel_schedule") not in [None, "", "미정"],
        state.get("travel_style") not in [None, "", "미정"]
    ])

    if extract_travel_info:
        if state.get("travel_place") not in [None, "", "미정"]:
            return "complete"
        elif state.get("need_place_search") is True:
            return "search"
        else:
            return "loop"

    return "complete"


def create_graph():
    graph = StateGraph(AgentState)

    # 노드 등록
    graph.add_node("travel_conversation", travel_conversation)
    graph.add_node("extract_info_llm_parser", extract_info_llm_parser)
    graph.add_node("extract_info_tool", ToolNode(tools=[extract_travel_info]))
    graph.add_node("search_place_tool", ToolNode(tools=[search_place_tool]))

    # 시작 지점
    graph.set_entry_point("travel_conversation")

    # travel_conversation → ToolNode
    graph.add_edge("travel_conversation", "extract_info_llm_parser")

    # ToolNode → travel_conversation (조건적 반복)
    graph.add_conditional_edges(
        "extract_info_llm_parser",
        path=should_conversation,
        path_map={
            "loop": "travel_conversation",
            "search": "search_place_tool",  # 예시로 장소 검색 ToolNode
            "complete": END
        }
    )

    graph.add_conditional_edges(  # 🔁 검색 노드도 종료되도록 분기 추가
        "search_place_tool",
        path=lambda state: END,
        path_map={END: END}
    )

    return graph.compile()


travel_conversation_graph = create_graph()
print(travel_conversation_graph.get_graph().draw_mermaid())


start_message = {
    "messages": [
        HumanMessage(content="여행을 가고 싶은데 어디가 좋을까요?")
    ]
}

result = travel_conversation_graph.invoke(start_message)
pprint(result)



