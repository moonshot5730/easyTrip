from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from app.cognitive_service.agent.travel_place_agent import \
    travel_place_conversation
from app.cognitive_service.agent_core.graph_condition import state_router
from app.cognitive_service.agent_core.graph_state import AgentState
from app.cognitive_service.agent_parser.extract_travel_place_parser import \
    extract_travel_place_llm_parser


def create_korea_easy_trip_graph():
    graph = StateGraph(AgentState)

    # ✅ 시작 라우터
    graph.add_node("state_router", state_router)

    # 노드 등록
    graph.add_node("travel_place_conversation", travel_place_conversation)
    graph.add_node("extract_travel_place_llm_parser", extract_travel_place_llm_parser)

    # 시작 지점
    graph.set_entry_point("state_router")

    # 시작 분기
    graph.add_conditional_edges(
        "state_router",
        path=lambda x: x["next_node"],
        path_map={
            "travel_place_conversation": "travel_place_conversation",
            "travel_plan_conversation": END,
            "travel_schedule_conversation": END,
            "travel_plan_share": END,
        },
    )
    graph.add_edge("travel_place_conversation", "extract_travel_place_llm_parser")
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)

agent_app = create_korea_easy_trip_graph()

if __name__ == "__main__":
    print(agent_app.get_graph().draw_mermaid())
