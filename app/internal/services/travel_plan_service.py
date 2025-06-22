from typing import Optional, List

from sqlalchemy import delete
from sqlmodel import select, Session

from app.core.infra.sqllite_conn import sqllite_engine
from app.models.travel_plan import TravelPlan


def create_plan(plan: TravelPlan) -> TravelPlan:
    with Session(sqllite_engine) as session:
        session.add(plan)
        session.commit()
        session.refresh(plan)
        return plan


def create_plans(plans: List[TravelPlan]) -> List[TravelPlan]:
    with Session(sqllite_engine) as session:
        session.add_all(plans)
        session.commit()
        return plans


def get_all_plan_by_session(session_id: str) -> Optional[List[TravelPlan]]:
    with Session(sqllite_engine) as session:
        result = session.exec(
            select(TravelPlan).where(TravelPlan.session_id == session_id)
        )
        plans = result.all()
        return plans if plans else None


def delete_plans_by_session(session_id: str) -> int:
    with Session(sqllite_engine) as session:
        result = session.exec(
            delete(TravelPlan).where(TravelPlan.session_id == session_id)
        )
        session.commit()
        return result.rowcount  # 삭제된 row 수 반환


def replace_plans_by_session(session_id: str, new_plans: List[TravelPlan]) -> List[TravelPlan]:
    with Session(sqllite_engine) as session:
        # 1. 기존 삭제
        session.exec(delete(TravelPlan).where(TravelPlan.session_id == session_id))
        session.commit()

        # 2. 새로 삽입
        session.add_all(new_plans)
        session.commit()

        # 3. 조회 및 반환
        result = session.exec(
            select(TravelPlan).where(TravelPlan.session_id == session_id)
        )
        return result.all()