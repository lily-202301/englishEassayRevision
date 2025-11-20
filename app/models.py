"""
SQLAlchemy ORM models for database tables.
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class Task(Base):
    """Task model for storing essay polishing requests and results."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    original_text = Column(Text, nullable=False, comment="原始英文文本")
    context = Column(Text, nullable=True, comment="上下文信息")
    status = Column(
        String(20),
        nullable=False,
        default="processing",
        comment="任务状态: processing/completed/failed"
    )
    report_json = Column(JSON, nullable=True, comment="完整的分析报告（JSON格式）")
    pdf_path = Column(String(500), nullable=True, comment="生成的PDF文件路径")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新时间"
    )

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, status={self.status})>"

