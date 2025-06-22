from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from app.cognitive_service.agent.travel_place_agent import \
    travel_place_conversation
from app.cognitive_service.agent.travel_plan_agent import travel_plan_conversation
from app.cognitive_service.agent.travel_search_summary_agent import travel_search_summary_conversation
from app.cognitive_service.agent_core.graph_condition import state_router, is_websearch
from app.cognitive_service.agent_core.graph_state import AgentState
from app.cognitive_service.agent_parser.extract_travel_place_parser import \
    extract_travel_place_llm_parser
from app.cognitive_service.agent_parser.extract_travel_plan_parser import extract_travel_plan_llm_parser


def create_korea_easy_trip_graph():
    graph = StateGraph(AgentState)

    # ✅ 시작 라우터
    graph.add_node("state_router", state_router)

    # 메인 노드 등록
    graph.add_node("travel_place_conversation", travel_place_conversation)   # 여행 장소 대화
    graph.add_node("travel_plan_conversation", travel_plan_conversation)   # 여행 장소 대화

    # 노드 이후 리프 노드
    graph.add_node("extract_travel_place_llm_parser", extract_travel_place_llm_parser) # 여행 정보 추출 파서
    graph.add_node("extract_travel_plan_llm_parser", extract_travel_plan_llm_parser) # 여행 정보 추출 파서
    graph.add_node("travel_search_summary_conversation", travel_search_summary_conversation) # 여행 정보 검색결과 요약

    # 시작 지점
    graph.set_entry_point("state_router")

    # 시작 분기
    graph.add_conditional_edges(
        "state_router",
        path=lambda x: x["next_node"],
        path_map={
            "travel_conversation": "travel_place_conversation",
            "travel_search": "travel_search_summary_conversation",
            "manage_calendar": END,
            "travel_plan": "travel_plan_conversation",
            "plan_share": END,
        },
    )

    graph.add_conditional_edges(
        "travel_place_conversation",
        path=is_websearch,
        path_map={
            "web_summary": "travel_search_summary_conversation",
            "extract": "extract_travel_place_llm_parser"
        }
    )
    graph.add_edge("travel_plan_conversation", "extract_travel_plan_llm_parser")

    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)

agent_app = create_korea_easy_trip_graph()

if __name__ == "__main__":
    print(agent_app.get_graph().draw_mermaid())
