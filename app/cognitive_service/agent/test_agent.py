from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, END


from typing import TypedDict, Optional

class AgentState(TypedDict):
    user_goal: Optional[str]
    stage: Optional[str]

def supervisor_router(state: AgentState) -> dict:
    """
    상태를 기반으로 분기 결정
    """
    if state.get("user_goal") is None:
        return {"__return__": "a_agent"}
    elif state.get("stage") == "search":
        return {"__return__": "b_agent"}
    else:
        return {"__return__": "c_agent"}

graph = StateGraph(AgentState)

def a_agent_fn(state: AgentState) -> dict:
    return {
        "messages": [AIMessage(content="✅ A Agent가 선택되었습니다.")],
    }

def b_agent_fn(state: AgentState) -> dict:
    return {
        "messages": [AIMessage(content="✅ B Agent가 선택되었습니다.")],
    }

def c_agent_fn(state: AgentState) -> dict:
    return {
        "messages": [AIMessage(content="✅ C Agent가 선택되었습니다.")],
    }

# 노드 등록
graph.add_node("a_agent", a_agent_fn)
graph.add_node("b_agent", b_agent_fn)
graph.add_node("c_agent", c_agent_fn)
graph.add_node("supervisor_router", supervisor_router)

# supervisor_router → 조건 분기
graph.add_conditional_edges(
    "supervisor_router",
    path=supervisor_router,
    path_map={
        "a_agent": "a_agent",
        "b_agent": "b_agent",
        "c_agent": "c_agent"
    }
)

# 각 에이전트는 끝으로 이동
graph.add_edge("a_agent", END)
graph.add_edge("b_agent", END)
graph.add_edge("c_agent", END)

# supervisor_router를 시작점으로 지정
graph.set_entry_point("supervisor_router")

# 그래프 컴파일
app = graph.compile()

state = {
    "user_goal": None,
    "stage": None
}

result = app.invoke(state)