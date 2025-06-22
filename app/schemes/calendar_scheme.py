from typing import List

from pydantic import BaseModel, Field


class TravelPlanInput(BaseModel):
    trip_date: str = Field(description="YYYY-MM-DD 형식의 여행 날짜")
    trip_schedule: str = Field(description="요약 일정 텍스트")

class TravelPlansInput(BaseModel):
    session_id: str
    plans: List[TravelPlanInput]