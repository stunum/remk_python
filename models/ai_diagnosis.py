"""
AI诊断信息管理模型
"""
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, CheckConstraint, DateTime, text, Numeric, Integer
from sqlalchemy.dialects.postgresql import JSONB

class AIDiagnosis(SQLModel, table=True):
    """AI诊断结果表:存储AI对眼底影像的诊断结果和相关信息"""
    __tablename__ = 'ai_diagnoses'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    image_id: int = Field(foreign_key="fundus_images.id", index=True)
    ai_model_name: Optional[str] = Field(default=None, max_length=100)
    ai_model_version: Optional[str] = Field(default=None, max_length=50)
    detect_file_path: str = Field(max_length=500)
    detect_file_name: str = Field(max_length=500)
    thumbnail_data: Optional[str] = Field(default=None, sa_column=Column(Text))
    diagnosis_result: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    confidence_score: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(5, 4)))
    processing_time_ms: Optional[int] = Field(default=None, sa_column=Column(Integer))
    severity_level: Optional[str] = Field(default=None, max_length=20)
    risk_assessment: Optional[str] = Field(default=None, sa_column=Column(Text))
    recommended_actions: Optional[str] = Field(default=None, sa_column=Column(Text))
    diagnostic_markers: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    processing_status: str = Field(default='completed', max_length=20)
    error_message: Optional[str] = Field(default=None, sa_column=Column(Text))
    reviewed_by: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    review_status: str = Field(default='pending', max_length=20, index=True)
    review_comments: Optional[str] = Field(default=None, sa_column=Column(Text))
    reviewed_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    
    __table_args__ = (
        CheckConstraint("confidence_score >= 0 AND confidence_score <= 1", name='check_confidence_score'),
        CheckConstraint("severity_level IN ('normal', 'mild', 'moderate', 'severe', 'critical')", name='check_severity_level'),
        CheckConstraint("processing_status IN ('pending', 'processing', 'completed', 'failed', 'timeout')", name='check_processing_status'),
        CheckConstraint("review_status IN ('pending', 'approved', 'rejected', 'modified')", name='check_review_status'),
    )
    
    def __repr__(self):
        return f"<AIDiagnosis(id={self.id}, image_id={self.image_id}, model='{self.ai_model_name}')>"

