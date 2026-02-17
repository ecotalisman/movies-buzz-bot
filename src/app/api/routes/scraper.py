from fastapi import APIRouter, Query

from src.app.schemas.scraper import ScrapedMovieOut, ReviewOut, ScraperResponse
from src.app.services.scraper import ScraperClient
from src.app.settings import settings

router = APIRouter()


@router.get("/top/scraper", response_model=ScraperResponse)
def top_scraper(limit: int = 15):
    client = ScraperClient(
        selenium_url=settings.selenium_url,
        base_url=settings.scraper_base_url,
    )
    scraped = client.search(limit=limit)
    results = []
    for m in scraped:
        results.append(ScrapedMovieOut(
            title=m.title,
            year=m.year,
            overview=m.overview,
            reviews=[ReviewOut(author=r.author, text=r.text) for r in m.reviews],
            page_url=m.page_url,
        ))
    return ScraperResponse(count=len(results), results=results)
