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


class SourceHTML(Base):
    __tablename__ = "source_html"

    id: Mapped[int] = mapped_column(
        BigInteger(), nullable=False, primary_key=True, autoincrement=True, comment="id"
    )
    source: Mapped[str] = mapped_column(
        String(1024), nullable=False, comment="source url"
    )
    source_hash: Mapped[str] = mapped_column(
        String(32), nullable=False, comment="shorter url"
    )
    content: Mapped[str] = mapped_column(Text(), comment="html")
    create_time: Mapped[datetime.datetime] = mapped_column(
        DateTime(),
        nullable=False,
        server_default=func.now(),
        comment="movie length(in seconds)",
    )

    __table_args__ = (
        UniqueConstraint("source_hash", name="uniq_idx_source_hash"),
    )
