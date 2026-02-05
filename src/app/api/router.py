from fastapi import APIRouter

from src.app.api.routes.search import router as search_router

api_router = APIRouter()
api_router.include_router(search_router, tags=["movies"])
