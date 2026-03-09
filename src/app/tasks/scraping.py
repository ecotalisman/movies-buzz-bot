from src.app.tasks.celery_app import celery_app
from src.app.settings import settings
from src.app.services.scraper import ScraperClient
from src.app.database.session import sync_engine
from src.app.database.models import Source, MovieItem

from sqlalchemy.orm import Session


@celery_app.task(bind=True, max_retries=3, name="src.app.tasks.scraping.run_scraper")
def run_scraper(self, limit: int = 15):
    client = ScraperClient(
        selenium_url=settings.selenium_url,
        base_url=settings.scraper_base_url,
    )
    try:
        scraped = client.search(limit)
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)

    session = Session(sync_engine)
    try:
        source = session.query(Source).filter_by(type="scraper").first()
        if source is None:
            source = Source(type="scraper", name="torrent_scraper", url=settings.scraper_base_url)

        session.add(source)
        session.flush()
        saved_count = 0

        for m in scraped:
            existing = session.query(MovieItem).filter(MovieItem.url == m.page_url).first()
            if existing:
                continue

            item = MovieItem(
                title=m.title,
                url=m.page_url,
                source_id=source.id,
                summary=m.overview or None,
                raw_text=m.overview or None,
            )
            session.add(item)
            saved_count += 1

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

    return {"scraped": len(scraped), "saved": saved_count}
