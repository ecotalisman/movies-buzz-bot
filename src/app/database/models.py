from sqlalchemy import String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List, Optional
from datetime import datetime
from src.app.database.base import Base


class Source(Base):
    __tablename__ = "sources"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[str] = mapped_column(String(50))
    name: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(Text)
    enabled: Mapped[bool] = mapped_column(default=True)
    movie_items: Mapped[List["MovieItem"]] = relationship(back_populates="source")


class MovieItem(Base):
    __tablename__ = "movie_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(512))
    url: Mapped[str] = mapped_column(Text)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_id: Mapped[int] = mapped_column(ForeignKey("sources.id"))
    published_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    raw_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source: Mapped["Source"] = relationship(back_populates="movie_items")
    posts: Mapped[List["Post"]] = relationship(back_populates="movie_item")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    movie_item_id: Mapped[int] = mapped_column(ForeignKey("movie_items.id"))
    generated_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    movie_item: Mapped["MovieItem"] = relationship(back_populates="posts")


class Keyword(Base):
    __tablename__ = "keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    word: Mapped[str] = mapped_column(String(255), unique=True)
