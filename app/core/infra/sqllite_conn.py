import aiosqlite
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel

from app.core.constant.path_constant import SQLLITE_DB


sqllite_engine = create_engine(f"sqlite:///{SQLLITE_DB}", echo=True)

def init_db():
    SQLModel.metadata.create_all(bind=sqllite_engine)