"""
患者信息管理模型
"""
from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, CheckConstraint, Text, Date, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB

class Patient(SQLModel, table=True):
    """患者信息表:存储患者的基本信息和医疗背景"""
    __tablename__ = 'patients'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    patient_id: str = Field(max_length=50, unique=True, index=True)
    name: str = Field(max_length=100, index=True)
    gender: Optional[str] = Field(default=None, max_length=10)
    birth_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    phone: Optional[str] = Field(default=None, max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, sa_column=Column(Text))
    emergency_contact: Optional[str] = Field(default=None, max_length=100)
    emergency_phone: Optional[str] = Field(default=None, max_length=20)
    medical_history: Optional[str] = Field(default=None, sa_column=Column(Text))
    allergies: Optional[str] = Field(default=None, sa_column=Column(Text))
    current_medications: Optional[str] = Field(default=None, sa_column=Column(Text))
    insurance_info: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    status: str = Field(default='active', max_length=20, index=True)
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
        CheckConstraint("gender IN ('male', 'female', 'other')", name='check_gender'),
        CheckConstraint("status IN ('active', 'inactive', 'deceased')", name='check_patient_status'),
    )
    
    def __repr__(self):
        return f"<Patient(id={self.id}, patient_id='{self.patient_id}', name='{self.name}')>"
