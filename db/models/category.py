# -*- coding: utf-8 -*-
import datetime
from sqlalchemy import (
    BigInteger,
    DateTime,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
    func,
    Index,
)
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class Category(Base):
    __tablename__ = "category"

    id: Mapped[int] = mapped_column(
        BigInteger(),
        nullable=False,
        primary_key=True,
        autoincrement=True,
        comment="category name",
    )
    name: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="category name"
    )
    create_time: Mapped[datetime.datetime] = mapped_column(
        DateTime, server_default=func.now(), comment="create time"
    )

    __table_args__ = (UniqueConstraint("id", "name", name="unix_id_name"),)


class CategoryMovie(Base):
    __tablename__ = "category_movie"

    id: Mapped[int] = mapped_column(
        BigInteger(),
        nullable=False,
        primary_key=True,
        autoincrement=True,
        comment="category name",
    )
    category_name: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="category name"
    )
    movie_id: Mapped[int] = mapped_column(
        BigInteger(), nullable=False, comment="movie id"
    )

    __table_args__ = (
        UniqueConstraint("category_name", "movie_id", name="uniq_idx_name_id"),
        Index("idx_category_movie", "movie_id", "category_name")
    )
