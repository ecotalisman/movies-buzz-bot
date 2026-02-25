from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import create_engine

from src.app.settings import settings
from src.app.database.base import Base

async_engine = create_async_engine(settings.async_db_url)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)
sync_engine = create_engine(settings.sync_db_url)


async def get_async_session():
    async with async_session_maker() as session:
        yield session
