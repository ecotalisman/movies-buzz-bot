from fastapi import APIRouter, Query

router = APIRouter()


@router.post("/scraper/trigger")
def trigger_scraper(limit: int = 15):
    from src.app.tasks.scraping import run_scraper
    task = run_scraper.delay(limit=limit)
    return {"task_id": task.id, "status": "submitted"}


@router.get("/scraper/status/{task_id}")
def trigger_get(task_id: str):
    from src.app.tasks.celery_app import celery_app
    task_result = celery_app.AsyncResult(task_id)
    response = {"task_id": task_id, "status": task_result.status}
    if task_result.ready():
        response["result"] = task_result.result
    return response
