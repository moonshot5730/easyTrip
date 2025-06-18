import graph_builder
from langgraph.graph import StateGraph

from app.cognitive_service.agent_langgraph.agent_condition import should_go_to_router
from app.cognitive_service.agent_langgraph.agent_node import intent_router_node
from app.cognitive_service.agent_langgraph.agent_state import AgentState
from app.cognitive_service.agent_prompt.intent_prompt_parser import extract_intent_as_action, travel_conversation
from app.cognitive_service.agent_tools.common_tool import search_travel_info_tool, create_travel_plan_tool, manage_travel_calendar_tool, share_travel_plan_tool, \
    travel_conversation_tool

def create_graph():
    graph_builder = StateGraph(AgentState)

    graph_builder.add_node("travel_conversation", travel_conversation)
    graph_builder.add_node("intent_router", intent_router_node)

    graph_builder.add_node("search_travel_info", search_travel_info_tool)
    graph_builder.add_node("create_travel_plan", create_travel_plan_tool)
    graph_builder.add_node("manage_travel_calendar", manage_travel_calendar_tool)
    graph_builder.add_node("share_travel_plan", share_travel_plan_tool)

    # 시작 지점
    graph_builder.set_entry_point("travel_conversation")

    # 대화 → intent 판단 or 계속 대화
    graph_builder.add_conditional_edges(
        source="travel_conversation",
        path=should_go_to_router,
        path_map={
            "intent_router": "intent_router",
            "travel_conversation": "travel_conversation"
        }
    )

    # intent_router → 툴 분기
    graph_builder.add_conditional_edges(
        source="intent_router",
        path=extract_intent_as_action,
        path_map={
            "search_travel_info": "search_travel_info",
            "create_travel_plan": "create_travel_plan",
            "manage_travel_calendar": "manage_travel_calendar",
            "share_travel_plan": "share_travel_plan",
            "travel_conversation": "travel_conversation"  # fallback
        }
    )

    # 각 툴 → 다시 대화로 돌아감
    for tool_name in [
        "search_travel_info", "create_travel_plan",
        "manage_travel_calendar", "share_travel_plan"
    ]:
        graph_builder.add_edge(tool_name, "travel_conversation")

    return graph_builder.compile()

agent_app = create_graph()

print(agent_app.get_graph().draw_mermaid())