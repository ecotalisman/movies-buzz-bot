from celery import Celery

from src.app.settings import settings

celery_app = Celery(
    "movies_buzz",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    imports=["src.app.tasks.scraping"],
)

celery_app.conf.beat_schedule = {
    "scrape-every-30-minutes": {
        "task": "src.app.tasks.scraping.run_scraper",
        "schedule": 30 * 60,
    },
}
