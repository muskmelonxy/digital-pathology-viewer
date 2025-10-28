import logging
from datetime import datetime
from typing import Any, Dict

from sqlalchemy import DateTime, Integer, String, Text, create_engine
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from config import Config

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


class Slide(Base):
    __tablename__ = "slides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    file_path: Mapped[str] = mapped_column(String(1024), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )
    slide_metadata: Mapped[Dict[str, Any] | None] = mapped_column(
        JSONB, nullable=True, default=dict, name="metadata"
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "file_path": self.file_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metadata": self.slide_metadata or {},
        }


engine = create_engine(Config.DATABASE_URL, future=True)

try:  # pragma: no cover - 连接可能在容器启动时暂不可用
    Base.metadata.create_all(engine)
except OperationalError as exc:
    logger.warning("数据库暂不可用，稍后将自动创建表结构：%s", exc)
