from datetime import datetime


def get_today_str() -> str:
    return datetime.now().strftime("%Y%m%d")
