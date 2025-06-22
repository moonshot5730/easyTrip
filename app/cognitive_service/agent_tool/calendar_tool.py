from dotenv.variables import Literal
from langchain_core.tools import tool

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.logger.logger_config import api_logger

@tool
def register_calendar(data: str) -> dict:
    """일정을 등록합니다. 입력은 JSON 문자열입니다."""
    # 여기에 SQLite INSERT 로직을 구현하면 됨
    return {"status": "success", "message": f"일정 등록 완료: {data}"}

@tool
def read_calendar(user_id: str) -> dict:
    """등록된 일정을 조회합니다."""
    # SQLite SELECT 로직
    return {"status": "success", "calendar": ["6/25 여행", "6/26 숙소 이동"]}

@tool
def update_calendar(update_info: str) -> dict:
    """일정을 업데이트합니다. 전체 삭제 후 재등록하는 방식입니다."""
    # SQLite DELETE + INSERT 로직
    return {"status": "success", "message": "일정 업데이트 완료"}

@tool
def delete_calendar(update_info: str) -> dict:
    """일정을 업데이트합니다. 전체 삭제 후 재등록하는 방식입니다."""
    # SQLite DELETE + INSERT 로직
    return {"status": "success", "message": "일정 업데이트 완료"}

calendar_tools = [register_calendar, read_calendar, update_calendar]