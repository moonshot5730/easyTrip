import graph_builder
from langgraph.checkpoint.memory import MemorySaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from app.cognitive_service.agent_core.graph_state import AgentState
from app.cognitive_service.agent_prompt.intent_prompt_parser import \
    travel_conversation


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
