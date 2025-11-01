"""
检查类型管理模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, Boolean, Integer, CheckConstraint, DateTime, text

class ExaminationType(SQLModel, table=True):
    """检查类型表:定义不同类型的眼底检查项目"""
    __tablename__ = 'examination_types'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    type_code: str = Field(max_length=20, unique=True, index=True)
    type_name: str = Field(max_length=100)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    body_part: Optional[str] = Field(default=None, max_length=50)
    duration_minutes: Optional[int] = Field(default=None, sa_column=Column(Integer))
    preparation_instructions: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text('CURRENT_TIMESTAMP'))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text('CURRENT_TIMESTAMP'))
    )
    
    __table_args__ = (
        CheckConstraint("duration_minutes >= 0", name='check_duration_minutes'),
    )
    
    def __repr__(self):
        return f"<ExaminationType(id={self.id}, type_code='{self.type_code}', type_name='{self.type_name}')>"
