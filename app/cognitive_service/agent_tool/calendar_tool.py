import asyncio
import json
from typing import List

from langchain_core.tools import tool

from app.internal.services.travel_plan_service import create_plans, get_all_plan_by_session, delete_plans_by_session
from app.models.travel_plan import TravelPlan
from app.schemes.calendar_scheme import TravelPlansInput, TravelPlanInput
from shared.format_util import convert_input_to_travel_plans



@tool("register_calendar", args_schema=TravelPlansInput)
def register_calendar(session_id: str, plans: List[TravelPlanInput]) -> dict:
    """여행 일정을 등록합니다. 이미 존재하면 등록 불가."""
    register_plans = convert_input_to_travel_plans(session_id, plans)

    return _register_calendar(session_id, register_plans)

def _register_calendar(session_id: str, travel_plans: List[TravelPlan]) -> dict:
    try:
        existing = get_all_plan_by_session(session_id=session_id)
        if existing:
            return {
                "status": "error",
                "message": f"{session_id} 세션에는 이미 등록된 일정이 있어요. 중복 등록할 수 없습니다. 등록된 일정 정보: {existing}"
            }

        created_plans = create_plans(travel_plans)
        return {
            "status": "success",
            "message": f"{created_plans} 일정들이 성공적으로 등록되었습니다."
        }
    except Exception as e:
        return {"status": "error", "message": f"입력 과정에서 예외가 발생했습니다. {str(e)}"}


@tool("read_calendar", args_schema=TravelPlansInput)
def read_calendar(session_id: str, plans: List[TravelPlanInput]) -> dict:
    """등록된 일정을 조회합니다."""

    return _read_calendar(session_id=session_id)

def _read_calendar(session_id: str) -> dict:
    try:
        existing = get_all_plan_by_session(session_id=session_id)
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
def update_calendar(session_id: str, plans: List[TravelPlanInput]) -> dict:
    """여행 일정을 수정합니다. 이미 존재하면 삭제 후 새로운 데이터 추가."""
    register_plans = convert_input_to_travel_plans(session_id, plans)

    return _update_calendar(session_id=session_id, new_plans=register_plans)

def _update_calendar(session_id: str, new_plans: List[TravelPlan]) -> dict:
    try:
        delete_results = delete_plans_by_session(session_id=session_id)
        if delete_results:
            created_plans = create_plans(new_plans)
            return {
                "status": "success",
                "message": f"{delete_results} 일정을 모두 삭제했습니다. {created_plans}를 새로 등록했습니다."
            }
        else:
            created_plans = create_plans(new_plans)
            return{
                "status": "success",
                "message": f"기존에 등록된 일정이 없습니다.{created_plans}을 새로 등록합니다."
            }
    except Exception as e:
        return {"status": "error", "message": f"수정 과정에서 예외가 발생했습니다. {str(e)}"}

@tool("delete_calendar", args_schema=TravelPlansInput)
def delete_calendar(session_id: str, plans: List[TravelPlanInput]) -> dict:
    """session_id로 등록된 일정을 모두 삭제합니다."""
    return _delete_calendar(session_id=session_id)


def _delete_calendar(session_id: str,) -> dict:
    try:
        delete_results =  delete_plans_by_session(session_id=session_id)
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