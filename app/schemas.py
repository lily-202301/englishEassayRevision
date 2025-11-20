"""
Pydantic schemas for request/response validation and AI output parsing.
"""
from typing import List, Optional
from pydantic import BaseModel, Field


class SentenceAnalysis(BaseModel):
    """Sentence-level analysis schema."""
    original: str = Field(..., description="原始句子")
    error: Optional[str] = Field(None, description="发现的错误或问题")
    correction: Optional[str] = Field(None, description="修正后的句子")
    suggestion: Optional[str] = Field(None, description="改进建议")


class FullReport(BaseModel):
    """Complete analysis report schema."""
    writing_goal_analysis: str = Field(..., description="写作目标分析")
    sentence_analysis: List[SentenceAnalysis] = Field(default_factory=list, description="句子级别分析列表")
    polished_version: str = Field(..., description="润色后的完整文本")


class TaskCreate(BaseModel):
    """Request schema for creating a new task."""
    original_text: str = Field(..., min_length=1, description="原始英文文本")
    context: Optional[str] = Field(None, description="上下文信息（如写作目标、受众等）")


class TaskResponse(BaseModel):
    """Response schema for task information."""
    id: int
    original_text: str
    context: Optional[str]
    status: str
    report_json: Optional[dict] = None
    pdf_path: Optional[str] = None

    class Config:
        from_attributes = True

