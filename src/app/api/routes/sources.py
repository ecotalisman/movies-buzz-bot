from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.app.database.session import get_async_session
from src.app.database.models import Source
from src.app.schemas.db import SourceCreate, SourceOut

router = APIRouter(prefix="/sources", tags=["sources"])


@router.get("/", response_model=list[SourceOut])
async def list_sources(session: AsyncSession = Depends(get_async_session)):
    statement = select(Source)
    result = await session.execute(statement)
    sources = result.scalars().all()
    return sources


@router.post("/", response_model=SourceOut, status_code=201)
async def create_source(payload: SourceCreate, session: AsyncSession = Depends(get_async_session)):
    obj = Source(**payload.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/{source_id}", response_model=SourceOut)
async def get_source(source_id: int, session: AsyncSession = Depends(get_async_session)):
    obj = await session.get(Source, source_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Source not found")
    return obj


@router.delete("/{source_id}", status_code=204)
async def delete_source(source_id: int, session: AsyncSession = Depends(get_async_session)):
    obj = await session.get(Source, source_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Source not found")
    await session.delete(obj)
    await session.commit()
    return None
