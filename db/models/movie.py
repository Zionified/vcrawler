# -*- coding: utf-8 -*-
import datetime
from sqlalchemy import (
    BigInteger,
    DateTime,
    Index,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Movie(Base):
    __tablename__ = "movie"

    id: Mapped[int] = mapped_column(
        BigInteger(), nullable=False, primary_key=True, autoincrement=True, comment="id"
    )

    name: Mapped[str] = mapped_column(String(64), nullable=False, comment="movie name")
    other_names: Mapped[str] = mapped_column(
        Text(), default="[]", nullable=False, comment="other movie names"
    )

    source: Mapped[str] = mapped_column(String(1024), nullable=False, comment="url")
    source_hash: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="shorter url"
    )

    release_year: Mapped[int] = mapped_column(
        SmallInteger(), nullable=False, comment="year"
    )
    release_date: Mapped[str] = mapped_column(
        Text(), nullable=False, comment="release date"
    )

    production_country: Mapped[str] = mapped_column(
        Text(), nullable=False, comment="country"
    )

    language: Mapped[str] = mapped_column(
        String(1024), nullable=False, comment="main language"
    )
    languages: Mapped[str] = mapped_column(
        String(1024), nullable=False, comment="other languages"
    )

    cover: Mapped[str] = mapped_column(Text(), default="[]", comment="movie cover")
    description: Mapped[str] = mapped_column(
        Text(), default="", comment="movie description"
    )

    video_length: Mapped[int] = mapped_column(
        BigInteger(), nullable=False, comment="movie length(in seconds)"
    )

    create_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        comment="movie length(in seconds)",
    )

    # source是网站链接，用作唯一索引
    __table_args__ = (
        UniqueConstraint("source_hash", name="uniq_idx_source_hash"),
        Index("idx_name_releaseyear_id", "name", "release_year", "id"),
    )
