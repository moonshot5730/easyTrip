import asyncio
import textwrap
from typing import List

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.cognitive_service.agent_core.graph_state import AgentState, get_last_human_message
from app.cognitive_service.agent_tool.calendar_tool import calendar_tools
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks


def manage_calendar_action(state: AgentState):
    user_query = state.get("user_query") or get_last_human_message(state.get("messages", []))

    system_prompt = textwrap.dedent("""
    당신은 일정 관리 에이전트입니다.
    아래 사용자 입력 정보와 요청 정보를 보고 적절한 일정 관련 Tool을 호출하세요.

    ### 사용 가능한 도구 목록 및 스키마
    - register_calendar: 사용자가 새로운 일정을 등록을 요청했습니다.
    - read_calendar: 사용자가 일정 조회를 요청했습니다.
    - update_calendar: 사용자가 기존 일정을 삭제하고 새 일정을 등록 혹은 수정을 요청했습니다.
    - delete_calendar: 사용자가 기존 일정을 삭제 요청했습니다.

    사용자의 요청:
    {user_query}

    사용자의 여행 일정 정보 :
    {travel_plan_dict}

    세션 식별자(session_id): {session_id}

    반드시 tool 값은 위에서 설명한 네 가지 중 하나여야 합니다.
    응답 시 반드시 위 도구 중 하나를 JSON 포맷으로 호출해야 하며, 다음 규칙을 지켜야 합니다:

    ```json
    {{
      "tool": "register_calendar",
      "data": {{
        "session_id": "세션 고유 ID (예: abc123)",
        "plans": [
          {{
            "trip_date": "YYYY-MM-DD 형식의 날짜 (예: 2025-07-20)",
            "trip_schedule": "요약 일정 텍스트 (예: 제주도 해변 산책)"
          }},
          {{
            "trip_date": "YYYY-MM-DD",
            "trip_schedule": "다음 일정"
          }}
        ]
      }}
    }}""").strip()

    messages = [
        SystemMessage(content=system_prompt.format(
            user_query=user_query,
            travel_plan_dict=state.get("travel_plan_dict", {}),
            session_id=state.get("session_id", ""),
        ))
    ]
    # LLM에게 도구 바인딩 후 실행
    response = precise_openai_fallbacks.bind_tools(calendar_tools).invoke(messages)
    api_logger.info(f"일정 추출 response 정보: {response}")

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

if __name__ == "__main__":
    async def run_test():
        test_state: AgentState = {
            "user_query": "이번 여행 일정을 등록해줘",
            "user_name": "문현준",
            "session_id": "test-session-123",
            "travel_plan_dict": {
                "2025-07-01": {
                    "오전: 한옥 마을 방문\n오후: 맛집 투어"
                },
                "2025-07-02": {
                    "오전: 지역 축제 참석\n오후: 야시장 및 야간 투어"
                },
                "2025-07-03": {
                    "오전: 산책과 힐링\n오후: 전통시장 방문"
                }
            },
            "messages": []
        }

        # 실행
        result_state = manage_calendar_action(test_state)

        print("\n일정 관리 결과:")
        for msg in result_state["messages"]:
            print(f"{msg}")

        print("\ncalendar_info:")
        for info in result_state.get("calendar_info", []):
            print(info)

    asyncio.run(run_test())