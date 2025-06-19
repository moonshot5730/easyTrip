import graph_builder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
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

    # 시작 지점
    graph_builder.set_entry_point("travel_conversation")

    # 끝 지점
    graph_builder.add_edge("travel_conversation", END)

    # 인메모리 체크포인터 등록
    checkpointer = MemorySaver()

    return graph_builder.compile(checkpointer=checkpointer)

agent_app = create_graph()

print(agent_app.get_graph().draw_mermaid())