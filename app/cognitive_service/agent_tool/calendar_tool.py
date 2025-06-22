import asyncio
import json
from typing import List

from langchain_core.tools import tool
from pydantic import BaseModel, Field

from app.internal.services.travel_plan_service import create_plans, get_all_plan_by_session, delete_plans_by_session
from app.models.travel_plan import TravelPlan
from shared.format_util import convert_input_to_travel_plans


class TravelPlanInput(BaseModel):
    trip_date: str = Field(description="YYYY-MM-DD 형식의 여행 날짜")
    trip_schedule: str = Field(description="요약 일정 텍스트")

class TravelPlansInput(BaseModel):
    session_id: str
    plans: List[TravelPlanInput]


@tool("register_calendar", args_schema=TravelPlansInput)
def register_calendar(llm_output: TravelPlansInput) -> dict:
    """여행 일정을 등록합니다. 이미 존재하면 등록 불가."""
    try:
        session_id, travel_plans = convert_input_to_travel_plans(llm_output)
    except Exception as e:
        return {"status": "error", "message": f"JSON 파싱 실패: {e}"}

    return asyncio.run(_register_calendar(session_id, travel_plans))

async def _register_calendar(session_id: str, travel_plans: List[TravelPlan]) -> dict:
    try:
        existing = await get_all_plan_by_session(session_id=session_id)
        if existing:
            return {
                "status": "error",
                "message": f"{session_id} 세션에는 이미 등록된 일정이 있어요. 중복 등록할 수 없습니다. 등록된 일정 정보: {existing}"
            }

        created_plans = await create_plans(travel_plans)
        return {
            "status": "success",
            "message": f"{created_plans} 일정들이 성공적으로 등록되었습니다."
        }
    except Exception as e:
        return {"status": "error", "message": f"입력 과정에서 예외가 발생했습니다. {str(e)}"}


@tool("read_calendar", args_schema=TravelPlansInput)
def read_calendar(llm_output: TravelPlansInput) -> dict:
    """등록된 일정을 조회합니다."""
    return asyncio.run(_read_calendar(session_id=llm_output.session_id))

async def _read_calendar(session_id: str) -> dict:
    try:
        existing = await get_all_plan_by_session(session_id=session_id)
        if existing:
            return {
            "status": "success",
            "message": f"{existing} 일정들이 성공적으로 조회되었습니다."
        }
        else:
            return{
                "status": "success",
                "message": f"{session_id}으로 등록된 일정이 없습니다. 새로 등록할까요?"
            }
    except Exception as e:
        return {"status": "error", "message": f"조회 과정에서 예외가 발생했습니다. {str(e)}"}

@tool("register_calendar", args_schema=TravelPlansInput)
def update_calendar(llm_output: TravelPlansInput) -> dict:
    """여행 일정을 수정합니다. 이미 존재하면 삭제 후 새로운 데이터 추가."""
    try:
        session_id, new_travel_plans = convert_input_to_travel_plans(llm_output)
    except Exception as e:
        return {"status": "error", "message": f"JSON 파싱 실패: {e}"}
    return asyncio.run(_update_calendar(session_id=session_id, new_plans=new_travel_plans))

async def _update_calendar(session_id: str, new_plans: List[TravelPlan]) -> dict:
    try:
        delete_results = await delete_plans_by_session(session_id=session_id)
        if delete_results:
            created_plans = await create_plans(new_plans)
            return {
                "status": "success",
                "message": f"{delete_results} 일정을 모두 삭제했습니다. {created_plans}를 새로 등록했습니다."
            }
        else:
            created_plans = await create_plans(new_plans)
            return{
                "status": "success",
                "message": f"기존에 등록된 일정이 없습니다.{created_plans}을 새로 등록합니다."
            }
    except Exception as e:
        return {"status": "error", "message": f"수정 과정에서 예외가 발생했습니다. {str(e)}"}

@tool("delete_calendar", args_schema=TravelPlansInput)
def delete_calendar(llm_output: TravelPlansInput) -> dict:
    """session_id로 등록된 일정을 모두 삭제합니다."""
    return asyncio.run(_delete_calendar(session_id=llm_output.session_id))


async def _delete_calendar(session_id: str,) -> dict:
    try:
        delete_results = await delete_plans_by_session(session_id=session_id)
        if delete_results:
            return {
                "status": "success",
                "message": f"{delete_results} 일정을 모두 삭제했습니다."
            }
        else:
            return {
                "status": "success",
                "message": f"{session_id}로 등록된 일정이 없습니다."
            }

    except Exception as e:
        return {"status": "error", "message": f"삭제 과정에서 예외가 발생했습니다. {str(e)}"}

calendar_tools = [register_calendar, read_calendar, update_calendar, delete_calendar]