from fastapi import FastAPI, Query

from src.app.logging_config import setup_logging
from src.app.settings import settings

from src.app.api.router import api_router
import logging

logger = logging.getLogger(__name__)

setup_logging(settings.log_level)
logger.info("Start FastAPI")
app = FastAPI(title="Movies Buzz API", version="0.1.0")
app.include_router(api_router)


@app.get("/health")
async def health(verbose: bool = Query(False, description="Show detailed status")):
    return {"status": "ok", "verbose": verbose}
