"""
检查记录管理模型
"""
from datetime import datetime, date, time
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Date, Time, Text, CheckConstraint, DateTime, text

class Examination(SQLModel, table=True):
    """检查记录表:记录每次眼底检查的基本信息和结果(可独立存在或与挂号关联)"""
    __tablename__ = 'examinations'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    examination_number: str = Field(max_length=50, unique=True, index=True)
    patient_id: int = Field(foreign_key="patients.id", index=True)
    examination_type_id: int = Field(foreign_key="examination_types.id")
    registration_id: Optional[int] = Field(default=None, foreign_key="registrations.id", index=True)
    doctor_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    technician_id: Optional[int] = Field(default=None, foreign_key="users.id")
    examination_date: date = Field(sa_column=Column(Date, nullable=False, index=True))
    examination_time: Optional[time] = Field(default=None, sa_column=Column(Time))
    eye_side: Optional[str] = Field(default=None, max_length=10)
    chief_complaint: Optional[str] = Field(default=None, sa_column=Column(Text))
    present_illness: Optional[str] = Field(default=None, sa_column=Column(Text))
    examination_findings: Optional[str] = Field(default=None, sa_column=Column(Text))
    preliminary_diagnosis: Optional[str] = Field(default=None, sa_column=Column(Text))
    recommendations: Optional[str] = Field(default=None, sa_column=Column(Text))
    follow_up_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    status: str = Field(default='pending', max_length=20, index=True)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text('CURRENT_TIMESTAMP'))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True, server_default=text('CURRENT_TIMESTAMP'))
    )
    created_by: Optional[int] = Field(default=None, foreign_key="users.id")
    updated_by: Optional[int] = Field(default=None, foreign_key="users.id")
    
    __table_args__ = (
        CheckConstraint("eye_side IN ('left', 'right', 'both')", name='check_eye_side'),
        CheckConstraint("status IN ('pending', 'in_progress', 'completed', 'cancelled')", name='check_examination_status'),
    )
    
    def __repr__(self):
        return f"<Examination(id={self.id}, examination_number='{self.examination_number}')>"
