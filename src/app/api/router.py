from fastapi import APIRouter

from src.app.api.routes.search import router as search_router
from src.app.api.routes.scraper import router as scraper_router
from src.app.api.routes.top import router as top_router

api_router = APIRouter()
api_router.include_router(search_router, tags=["movies"])
api_router.include_router(scraper_router, tags=["scraper"])
api_router.include_router(top_router, tags=["top_router"])
