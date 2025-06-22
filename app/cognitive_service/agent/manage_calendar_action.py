from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.cognitive_service.agent_core.graph_state import AgentState, get_last_human_message
from app.cognitive_service.agent_tool.calendar_tool import calendar_tools
from app.external.openai.openai_client import precise_openai_fallbacks


def manage_calendar_action(state: AgentState):
    user_query = get_last_human_message(state.get("messages", []))

    system_prompt = """
    당신은 일정 관리 에이전트입니다.
    아래 사용자 요청을 보고 적절한 일정 관련 Tool을 호출하세요.
    가능한 도구:
    - register_calendar
    - read_calendar
    - update_calendar

    사용자의 요청:
    {user_query}
    """

    messages = [
        SystemMessage(content=system_prompt.format(user_query=user_query)),
        HumanMessage(content=user_query),
    ]

    # LLM에게 도구 바인딩 후 실행
    response = precise_openai_fallbacks.bind_tools(calendar_tools).invoke(messages)

    # ToolCall 결과 추출
    tool_calls = getattr(response, "tool_calls", None)
    tool_results = []
    tool_messages = []

    if tool_calls:
        for call in tool_calls:
            tool_name = call["name"]
            args = call["args"]

            # SQLite 내부 함수 실행
            tool_result = next(
                (tool.invoke(args) for tool in calendar_tools if tool.name == tool_name),
                {"status": "error", "message": f"Unknown tool: {tool_name}"}
            )

            tool_results.append(tool_result)
            tool_messages.append(AIMessage(content=str(tool_result)))

    return {
        **state,
        "messages": state["messages"] + [HumanMessage(content=user_query)] + tool_messages,
        "calendar_info": tool_results,
    }