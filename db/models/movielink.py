#-*- coding: utf-8 -*-
from datetime import datetime
from sqlalchemy import BigInteger, DateTime, Index, SmallInteger, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base


class MovieLink(Base):
    __tablename__ = "movie_link"
    
    # TYPE_DOWNLOADABLE = 0
    # TYPE_M3U8 = 1
    
    id: Mapped[int] = mapped_column(BigInteger(), nullable=False, primary_key=True, autoincrement=True, comment="id")
    movie_id: Mapped[int] = mapped_column(BigInteger(), nullable=False,  comment="movie id")
    link: Mapped[str] = mapped_column(Text(), nullable=False,  comment="download url")
    
    __table_args__ = (
        Index("idx_movieid", "movie_id"),
    )