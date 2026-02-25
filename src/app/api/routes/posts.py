from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.app.database.session import get_async_session
from src.app.database.models import Post
from src.app.schemas.db import PostCreate, PostOut

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/", response_model=list[PostOut])
async def list_posts(session: AsyncSession = Depends(get_async_session)):
    statement = select(Post)
    result = await session.execute(statement)
    posts = result.scalars().all()
    return posts


@router.post("/", response_model=PostOut, status_code=201)
async def create_post(payload: PostCreate, session: AsyncSession = Depends(get_async_session)):
    obj = Post(**payload.model_dump())
    session.add(obj)
    await session.commit()
    await session.refresh(obj)
    return obj


@router.get("/{post_id}", response_model=PostOut)
async def get_post(post_id: int, session: AsyncSession = Depends(get_async_session)):
    obj = await session.get(Post, post_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return obj


@router.delete("/{post_id}", status_code=204)
async def delete_post(post_id: int, session: AsyncSession = Depends(get_async_session)):
    obj = await session.get(Post, post_id)
    if obj is None:
        raise HTTPException(status_code=404, detail="Post not found")
    await session.delete(obj)
    await session.commit()
    return None
