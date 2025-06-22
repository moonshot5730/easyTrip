from datetime import date
from typing import Optional, List

from sqlmodel import SQLModel, Field

class TravelPlan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: str = Field(index=True)

    trip_date: Optional[str] = None
    trip_schedule: Optional[str] = None  # 요약 일정 텍스트
    created_at: Optional[str] = Field(default_factory=lambda: date.today().isoformat())
