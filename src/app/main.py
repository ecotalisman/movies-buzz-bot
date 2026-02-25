from fastapi import FastAPI, Query
from contextlib import asynccontextmanager

from sqlalchemy import text

from src.app.logging_config import setup_logging
from src.app.settings import settings

from src.app.api.router import api_router
from src.app.database.session import async_engine
import logging

logger = logging.getLogger(__name__)

setup_logging(settings.log_level)
logger.info("Start FastAPI")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Startup: checking DB connection...")
    async with async_engine.connect() as conn:
        await conn.execute(text("SELECT 1"))

    logger.info("Startup: DB connection OK")

    yield

    logger.info("Shutdown: disposing async engine...")
    await async_engine.dispose()
    logger.info("Shutdown: done")

app = FastAPI(title="Movies Buzz API", version="0.1.0", lifespan=lifespan)
app.include_router(api_router)


@app.get("/health")
async def health(verbose: bool = Query(False, description="Show detailed status")):
    return {"status": "ok", "verbose": verbose}
