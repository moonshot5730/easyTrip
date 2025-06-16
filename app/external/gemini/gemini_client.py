import os

from google import genai
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from app.core.constant.env_constant import GOOGLE_API_KEY
from app.core.logger.logger_config import get_logger

logger = get_logger()

def test_gemini_key() -> bool:
    """
    OpenAI API 키의 유효성을 테스트합니다.
    모델 목록 호출을 통해 키가 유효한지 확인합니다.
    """
    gemini_api_key = os.environ.get(GOOGLE_API_KEY)

    if gemini_api_key:
        logger.info(f"등록된 Gemini 키 요약 정보: {gemini_api_key[:5]}...{gemini_api_key[-5:]}")
    else:
        logger.error(f"오류: {GOOGLE_API_KEY} 환경 변수가 설정되지 않았습니다.")

    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api_key)
        test_msg = HumanMessage(content="Hello!")
        response = llm.invoke([test_msg])
        content = getattr(response, "content", None) or getattr(response, "generations", None)
        if not content:
            logger.critical("GEMINI API의 응답 내용이 없습니다.")
            return False

        logger.info(f"Gemini API 키가 유효하며 정상 응답이 확인되었습니다. 응답 내용 : {content}")
        return True
    except Exception as e:
        logger.error(f"❌ Gemini 호출 중 예외 발생: {e}")
        return False