from fastapi import APIRouter

from src.app.api.routes.search import router as search_router
from src.app.api.routes.scraper import router as scraper_router
from src.app.api.routes.top import router as top_router

from src.app.api.routes.sources import router as sources_router
from src.app.api.routes.keywords import router as keywords_router
from src.app.api.routes.posts import router as posts_router

api_router = APIRouter()
api_router.include_router(search_router, tags=["movies"])
api_router.include_router(scraper_router, tags=["scraper"])
api_router.include_router(top_router, tags=["top"])
api_router.include_router(sources_router, tags=["sources"])
api_router.include_router(keywords_router, tags=["keywords"])
api_router.include_router(posts_router, tags=["posts"])
