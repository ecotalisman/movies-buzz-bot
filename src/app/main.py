from fastapi import FastAPI, Query

from src.app.api.router import api_router
app = FastAPI(title="Movies Buzz API", version="0.1.0")
app.include_router(api_router)


@app.get("/health")
async def health(verbose: bool = Query(False, description="Show detailed status")):
    return {"status": "ok", "verbose": verbose}
