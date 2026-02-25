from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.app.database.session import get_async_session
from src.app.database.models import Keyword
from src.app.schemas.db import KeywordCreate, KeywordOut

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.get("/", response_model=list[KeywordOut])
async def list_keywords(session: AsyncSession = Depends(get_async_session)):
    statement = select(Keyword)
    result = await session.execute(statement)
    keywords = result.scalars().all()
    return keywords


@router.post("/", response_model=KeywordOut, status_code=201)
async def create_keyword(payload: KeywordCreate, session: AsyncSession = Depends(get_async_session)):
    obj = Keyword(**payload.model_dump())
    session.add(obj)
    try:
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(status_code=409, detail="Keyword already exists")

    await session.refresh(obj)
    return obj


@router.delete("/{keyword_id}", status_code=204)
async def delete_keyword(keyword_id: int, session: AsyncSession = Depends(get_async_session)):
    obj = await session.get(Keyword, keyword_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Keyword not found")
    await session.delete(obj)
    await session.commit()
    return None

