import zoneinfo
from datetime import datetime, timedelta


def get_today_str() -> str:
    return datetime.now().strftime("%Y%m%d")


def get_kst_timestamp_label():
    kst = datetime.now(tz=zoneinfo.ZoneInfo("Asia/Seoul"))
    return f"{kst.month}월 {kst.day}일 {kst.hour}시"


def get_kst_year_month_date_label():
    kst = datetime.now(tz=zoneinfo.ZoneInfo("Asia/Seoul"))
    return f"{kst.year}년 {kst.month}월 {kst.day}일"
