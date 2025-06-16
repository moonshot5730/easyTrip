from pathlib import Path

# 기준이 되는 루트 디렉토리 최상위 폴더)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

ENV_PATH = BASE_DIR / ".env"

LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "app.log"
