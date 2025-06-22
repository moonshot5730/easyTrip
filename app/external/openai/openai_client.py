import os

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from openai import AuthenticationError, OpenAI

from app.core.constant.env_constant import OPENAI_API_KEY
from app.core.logger.logger_config import get_logger

logger = get_logger()


def test_openai_key() -> bool:
    """
    OpenAI API 키의 유효성을 테스트합니다.
    모델 목록 호출을 통해 키가 유효한지 확인합니다.
    """
    openai_api_key = os.environ.get(OPENAI_API_KEY)

    if not openai_api_key:
        logger.error("오류: OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        return False

    logger.info(
        f"등록된 Openai 키 요약 정보: {openai_api_key[:5]}...{openai_api_key[-5:]}"
    )

    try:
        openai_model = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0,
            openai_api_key=openai_api_key,
        )
        messages = [
            SystemMessage(content="You are a testing assistant."),
            HumanMessage(content="Hello!"),
        ]
        resp = openai_model.invoke(messages)
        content = getattr(resp, "content", None)
        if not content:
            logger.critical("Open AI의 응답이 없습니다.")
            return False
        logger.info(f"OpenAI 키가 유효하며 응답을 확인했습니다. 응답 내용: {content}")
        return True
    except AuthenticationError:
        logger.error("유효하지 않은 OpenAI API 키입니다.")
        return False
    except Exception as e:
        logger.error(
            f"OpenAI API 테스트 호출 과정에서 예상치 못한 예외가 발생했습니다: {e}"
        )
        return False


creative_llm_nano = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0.8,
    streaming=True,
)

creative_openai_mini = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0.8,
    streaming=True,
)

creative_openai_fallbacks = creative_llm_nano.with_fallbacks([creative_openai_mini])

precise_llm_nano = ChatOpenAI(
    model="gpt-4.1-nano",
    temperature=0,
    streaming=True,
)

precise_llm_mini = ChatOpenAI(
    model="gpt-4.1-mini",
    temperature=0,
    streaming=True,
)

precise_openai_fallbacks = precise_llm_mini.with_fallbacks([precise_llm_nano])
