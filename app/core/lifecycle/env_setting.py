import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from app.core.constant.path_constant import ENV_PATH
from app.core.logger.logger_config import get_logger

logger = get_logger()


def load_env():
    env_file = Path(ENV_PATH)

    if not env_file.exists():
        logger.error(
            f"환경 변수 파일 {env_file.resolve()}이 존재하지 않습니다. 환경 변수 파일을 확인해주세요. 시스템을 종료합니다."
        )
        sys.exit(1)

    load_dotenv(dotenv_path=env_file)
    logger.info(f"환경 파일 {env_file} 로드 완료했습니다.")
