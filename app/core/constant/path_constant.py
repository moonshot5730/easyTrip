from pathlib import Path

from shared.datetime_util import get_today_str

# 기준이 되는 루트 디렉토리 최상위 폴더)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

ENV_PATH = BASE_DIR / ".env"

LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / f"api_{get_today_str()}.log"

SQLLITE_DIR = BASE_DIR / "sqllite"
SQLLITE_DB = SQLLITE_DIR / "trip_plan.db"

SHARE_BASE_PATH = BASE_DIR / "tmp" / "share_html"
SHARE_BASE_URL = "http://localhost:8000/trip/plan/share"
