import aiosqlite
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from app.core.constant.path_constant import SQLLITE_DB


sqllite_aio_engine = create_async_engine(f"sqlite+aiosqlite:///{SQLLITE_DB}", echo=True)

async def init_db():
    async with sqllite_aio_engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)