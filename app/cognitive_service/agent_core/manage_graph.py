from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from app.cognitive_service.agent.travel_conversation_agent import travel_conversation
from app.cognitive_service.agent_core.graph_condition import state_router

from app.cognitive_service.agent_core.graph_state import AgentState
from app.cognitive_service.agent_parser.travel_conversation_json_parser import extract_info_llm_parser


def create_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("travel_conversation", travel_conversation)

    # 시작 지점
    graph_builder.set_entry_point("travel_conversation")

    # 끝 지점
    graph_builder.add_edge("travel_conversation", END)

    # 인메모리 체크포인터 등록
    checkpointer = MemorySaver()
    return graph_builder.compile(checkpointer=checkpointer)


# agent_app = create_graph()


def create_korea_easy_trip_graph():
    graph = StateGraph(AgentState)

    # ✅ 시작 라우터
    graph.add_node("state_router", state_router)

    # 노드 등록
    graph.add_node("travel_conversation", travel_conversation)
    graph.add_node("travel_search", travel_conversation)
    # graph.add_node("travel_schedule_conversation", travel_conversation)
    # graph.add_node("travel_plan_conversation", travel_conversation)
    # graph.add_node("travel_plan_share", travel_conversation)

    graph.add_node("extract_info_llm_parser", extract_info_llm_parser)

    # 시작 지점
    graph.set_entry_point("state_router")

    # 시작 분기
    graph.add_conditional_edges(
        "state_router",
        path=lambda x: x["next_node"],
        path_map={
            "travel_place_conversation": "travel_conversation",
            "travel_search": END,
            "travel_schedule_conversation": END,
            "travel_plan_conversation": END,
            "travel_plan_share": END,
        }
    )
    graph.add_edge("travel_conversation", "extract_info_llm_parser")
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)

agent_app = create_korea_easy_trip_graph()