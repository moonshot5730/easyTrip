import asyncio
import textwrap
from typing import List

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from app.cognitive_service.agent_core.graph_state import AgentState, get_last_human_message
from app.cognitive_service.agent_tool.calendar_tool import calendar_tools
from app.core.infra.sqllite_conn import init_db
from app.core.logger.logger_config import api_logger
from app.external.openai.openai_client import precise_openai_fallbacks


def manage_calendar_action(state: AgentState):
    user_query = state.get("user_query") or get_last_human_message(state.get("messages", []))

    system_prompt = textwrap.dedent("""
    당신은 일정 관리 에이전트입니다.
    아래 사용자의 요청 정보에서 의도를 분석해서 적절한 일정 관련 Tool을 호출하세요.

    사용 가능한 도구 목록 및 호출 조건:
    - register_calendar: 사용자가 새로운 일정을 **등록하거나 추가**해달라고 요청한 경우  
        (예: "일정 등록해줘", "새 일정 넣어줘", "여행 계획 추가해줘")
    - read_calendar: 사용자가 **등록된 일정을 조회하거나 확인**하려는 경우  
        (예: "내 일정 보여줘", "무슨 일정이 있는지 알려줘")
    - update_calendar: 사용자가 기존 일정을 **수정하거나 변경, 갱신**하려는 경우  
        (예: "일정을 바꿔줘", "수정할게", "갱신해줘", "일정 변경", "새롭게 수정해줘")
    - delete_calendar: 사용자가 기존 일정을 **삭제하거나 지워달라고** 요청한 경우  
        (예: "이 일정 삭제해줘", "지워줘", "계획 없애줘")

    사용자의 요청:
    {user_query}

    사용자의 여행 일정 정보 :
    {travel_plan_dict}

    세션 식별자(session_id): {session_id}

    아래 도구 중 하나를 반드시 호출하세요.
    register_calendar, read_calendar, update_calendar, delete_calendar
    
    아래의 JSON응답을 도구 인자 정보로 활용하세요.
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
    api_logger.info(f"tool_calls 정보: {tool_calls}")

    tool_results = []
    tool_messages = []

    if tool_calls:
        for call in tool_calls:
            tool_name = call["name"]
            args = call["args"]  # 딕셔너리 형태

            # 해당 tool 찾아서 kwargs로 언팩 호출
            tool_instance = next((tool for tool in calendar_tools if tool.name == tool_name), None)

            if tool_instance:
                try:
                    tool_result = tool_instance.invoke(args)  # ✅ 핵심 수정
                except Exception as e:
                    tool_result = {"status": "error", "message": str(e)}
            else:
                tool_result = {"status": "error", "message": f"Unknown tool: {tool_name}"}

            tool_results.append(tool_result)
            tool_messages.append(AIMessage(content=str(tool_result)))

    return {
        **state,
        "messages": state["messages"] + [HumanMessage(content=user_query)] + tool_messages,
        "calendar_info": tool_results,
    }

if __name__ == "__main__":
    init_db()
    async def run_test():
        test_state: AgentState = {
            "user_query": "이번 여행 일정을 수정해줘",
            "user_name": "문현준",
            "session_id": "test-session-123",
            "travel_plan_dict": {
                "2025-07-08": {
                    "오전: 한옥 마을 방문\n오후: 맛집 투어"
                },
                "2025-07-09": {
                    "오전: 지역 축제 참석\n오후: 야시장 및 야간 투어"
                },
                "2025-07-10": {
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