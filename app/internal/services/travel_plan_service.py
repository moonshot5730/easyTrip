from typing import Optional, List

from sqlalchemy import delete
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.core.infra.sqllite_conn import sqllite_aio_engine
from app.models.travel_plan import TravelPlan


async def create_plan(plan: TravelPlan) -> TravelPlan:
    async with AsyncSession(sqllite_aio_engine) as session:
        session.add(plan)
        await session.commit()
        await session.refresh(plan)
        return plan


async def create_plans(plans: List[TravelPlan]) -> List[TravelPlan]:
    async with AsyncSession(sqllite_aio_engine) as session:
        session.add_all(plans)  # 여러 개 추가
        await session.commit()

        return plans


async def get_all_plan_by_session(session_id: str) -> Optional[List[TravelPlan]]:
    async with AsyncSession(sqllite_aio_engine) as session:
        result = await session.exec(
            select(TravelPlan).where(TravelPlan.session_id == session_id)
        )
        plans = result.all()
        return plans if plans else None



async def delete_plans_by_session(session_id: str) -> int:
    async with AsyncSession(sqllite_aio_engine) as session:
        result = await session.exec(
            delete(TravelPlan).where(TravelPlan.session_id == session_id)
        )
        await session.commit()
        return result.rowcount



async def replace_plans_by_session(session_id: str, new_plans: List[TravelPlan]) -> List[TravelPlan]:
    async with AsyncSession(sqllite_aio_engine) as session:
        # 1. 기존 삭제
        await delete_plans_by_session(session_id=session_id)
        await create_plans(new_plans)
        await session.commit()

        # 3. 새로 삽입된 결과 조회 및 반환
        result = await session.exec(
            select(TravelPlan).where(TravelPlan.session_id == session_id)
        )
        return result.all()