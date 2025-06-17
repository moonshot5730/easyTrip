# 공통 출력 함수
from typing import Dict, Any

from langchain_core.runnables import RunnableLambda


def make_print_tool(label: str):
    def tool(state: Dict[str, Any]):
        print(f"[{label}] 실행됨 - 입력: {state}")
        return state  # 상태 그대로 반환
    return RunnableLambda(tool)

# 각 노드 도구 정의
search_places_tool = make_print_tool("🔍 여행 장소 검색")
generate_plan_tool = make_print_tool("🗺️ 여행 계획 생성")
calendar_tool = make_print_tool("📅 일정 관리")
share_tool = make_print_tool("🔗 계획 공유")
end_node = make_print_tool("✅ 기타 or 종료")