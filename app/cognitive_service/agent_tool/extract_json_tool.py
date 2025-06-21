# 공통 출력 함수
from typing import Any, Dict

from langchain.tools import tool
from langchain_core.runnables import RunnableLambda
from langgraph.types import Command

from app.core.logger.logger_config import get_logger

logger = get_logger()

def make_print_tool(label: str):
    def tool(state: Dict[str, Any]):
        print(f"[{label}] 실행됨 - 입력: {state}")
        return state  # 상태 그대로 반환

    return RunnableLambda(tool)


# 각 노드 도구 정의
search_travel_info_tool = make_print_tool("🔍 여행 장소 검색")
create_travel_plan_tool = make_print_tool("🗺️ 여행 계획 생성")
manage_travel_calendar_tool = make_print_tool("📅 일정 관리")
share_travel_plan_tool = make_print_tool("🔗 계획 공유")
travel_conversation_tool = make_print_tool("✅ 기타 or 여행 대화 진행")


@tool
def extract_travel_info(text: str) -> Command:
    """예시 정규식 or LLM 응답 기반 처리"""

    # return {
    #     "travel_place": "부산",
    #     "travel_schedule": "2025-08-01 ~ 2025-08-03",
    #     "travel_style": "자연과 휴식"
    # }
    logger.info(f"extract_travel_info TOOL을 호출 했습니다! 입력된 정보: {text}")

    return Command(
        update={
            "travel_place": "부산",
            "travel_schedule": "2025-08-01 ~ 2025-08-03",
            "travel_style": "자연과 휴식"
        })