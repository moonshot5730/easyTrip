from pathlib import Path

# 기준이 되는 루트 디렉토리 (예: main.py 기준으로 ../ 상위 폴더)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# .env 파일 경로
ENV_PATH = BASE_DIR / ".env"

# 로그 파일 경로
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"
