"""
随访管理模型
"""
from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Date, Text, CheckConstraint, DateTime, text, Boolean, Integer

class FollowUp(SQLModel, table=True):
    """随访管理表:管理患者的随访计划和执行情况"""
    __tablename__ = 'follow_ups'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: int = Field(foreign_key="patients.id", index=True)
    original_examination_id: Optional[int] = Field(default=None, foreign_key="examinations.id")
    follow_up_type: str = Field(max_length=50)
    scheduled_date: date = Field(sa_column=Column(Date, nullable=False))
    actual_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    follow_up_interval_days: Optional[int] = Field(default=None, sa_column=Column(Integer))
    priority: Optional[str] = Field(default=None, max_length=20)
    status: str = Field(default='scheduled', max_length=20, index=True)
    reminder_sent: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    reminder_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    follow_up_notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    outcome: Optional[str] = Field(default=None, sa_column=Column(Text))
    next_follow_up_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    assigned_doctor_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    
    __table_args__ = (
        CheckConstraint("priority IN ('low', 'medium', 'high', 'urgent')", name='check_priority'),
        CheckConstraint("status IN ('scheduled', 'completed', 'missed', 'cancelled', 'rescheduled')", name='check_followup_status'),
    )
    
    def __repr__(self):
        return f"<FollowUp(id={self.id}, patient_id={self.patient_id}, type='{self.follow_up_type}')>"

