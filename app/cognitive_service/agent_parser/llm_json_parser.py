import json

from app.cognitive_service.agent_core.graph_state import AgentState
from app.core.logger.logger_config import get_logger
from app.external.openai.openai_client import precise_llm_nano

logger = get_logger()

def extract_info_llm_parser(state: AgentState):
    raw = state.get("travel_conversation_raw_output")
    user_input = getattr(raw, "content", raw) if raw else ""

    prompt = f"""
    아래 문장에서 여행 장소, 일정, 스타일을 JSON으로 추출해줘:
    {user_input}
    """

    response = precise_llm_nano.invoke(prompt)

    parsed = json.loads(response.content)  # 또는 pydantic parser 사용

    logger.info(f"응답 정보에서 필요한 정보를 파싱합니다. : 프롬프트 : {prompt} 응답 정보: {response.content} 파싱된 정보: {parsed}")
    return {
        "travel_place": parsed.get("travel_place"),
        "travel_schedule": parsed.get("travel_schedule"),
        "travel_style": parsed.get("travel_style"),
    }