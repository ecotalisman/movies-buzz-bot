from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class _OutBase(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SourceCreate(BaseModel):
    type: str
    name: str
    url: str
    enabled: bool


class SourceOut(_OutBase, SourceCreate):
    id: int


class KeywordCreate(BaseModel):
    word: str


class KeywordOut(_OutBase, KeywordCreate):
    id: int


class PostCreate(BaseModel):
    movie_item_id: int
    status: str


class PostOut(_OutBase, PostCreate):
    id: int
    generated_text: Optional[str] = None
    published_at: Optional[datetime] = None
