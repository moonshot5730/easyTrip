import os
import sys

import requests
from google import genai
from openai import OpenAI, AuthenticationError

from app.core.constant.env_constant import REQUIRED_KEY
from app.core.logger.logger_config import get_logger
from app.external.gemini.gemini_client import test_gemini_key
from app.external.openai.openai_client import test_openai_key

logger = get_logger()

def _validate_env_keys():
    missing_keys = [key for key in REQUIRED_KEY if not os.environ.get(key)]

    if missing_keys:
        logger.error(
            f"다음 필수 환경 변수가 설정되지 않았습니다:  {', '.join(missing_keys)} 해당 환경 변수는 필수 정보입니다. 시스템을 종료합니다."
        )
        sys.exit(1)
    logger.info("모든 필수 환경 변수가 설정되었습니다. :)")

def validate_llm_keys():
    _validate_env_keys()
    openai_ok = test_openai_key()
    gemini_ok = test_gemini_key()

    if not openai_ok or not gemini_ok:
        logger.critical("입력된 API 키 중 하나 이상이 유효하지 않아 서버를 종료합니다.")
        sys.exit(1)

    logger.info(f"{REQUIRED_KEY}의 키들이 유효합니다.")