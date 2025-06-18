import graph_builder
from langgraph.graph import StateGraph

from app.cognitive_service.agent_langgraph.agent_router import intent_router_node
from app.cognitive_service.agent_langgraph.agent_state import AgentState
from app.cognitive_service.agent_prompt.intent_prompt_parser import extract_intent_as_action
from app.cognitive_service.agent_tools.common_tool import search_travel_info_tool, create_travel_plan_tool, manage_travel_calendar_tool, share_travel_plan_tool, \
    travel_conversation_tool

def create_graph():
    graph_builder = StateGraph(AgentState)
    graph_builder.add_node("intent_router", intent_router_node)

    graph_builder.add_node("search_travel_info", search_travel_info_tool)
    graph_builder.add_node("create_travel_plan", create_travel_plan_tool)
    graph_builder.add_node("manage_travel_calendar", manage_travel_calendar_tool)
    graph_builder.add_node("share_travel_plan", share_travel_plan_tool)
    graph_builder.add_node("travel_conversation", travel_conversation_tool)

    graph_builder.set_entry_point("intent_router")

    graph_builder.add_conditional_edges(
        source="intent_router",
        path=extract_intent_as_action,
        path_map={
            "search_travel_info": "search_travel_info",
            "create_travel_plan": "create_travel_plan",
            "manage_travel_calendar": "manage_travel_calendar",
            "share_travel_plan": "share_travel_plan",
            "travel_conversation": "travel_conversation"
        }
    )
    return graph_builder.compile()

agent_app = create_graph()
