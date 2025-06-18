from langchain_core.runnables import RunnableLambda

from app.cognitive_service.agent_llm.llm_models import precise_llm_nano
from app.cognitive_service.agent_prompt.intent_prompt_parser import intent_prompt_template, intent_parser
from app.core.logger.logger_config import get_logger

logger = get_logger()

def safe_intent_router(input: dict) -> dict:
    intent_router = (intent_prompt_template | precise_llm_nano).invoke(input)

    try:
        # output_parser.parse expects raw LLM string output
        parsed = intent_parser.parse(intent_router.content)
        return parsed.dict()
    except Exception as e:
        print(f"[Router] JSON 파싱 실패 → fallback: end ({e})")
        return {
            "action": "travel_conversation",
            "keywords": []
        }

intent_router_node = RunnableLambda(safe_intent_router)