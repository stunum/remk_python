"""
挂号登记管理模型
"""
from datetime import datetime, date, time
from typing import Optional
from decimal import Decimal
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Date, Time, Text, CheckConstraint, Numeric, Integer, DateTime, text

class Registration(SQLModel, table=True):
    """挂号表:管理患者挂号与预约流程(可选择性地关联检查记录)"""
    __tablename__ = 'registrations'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    registration_number: str = Field(max_length=50, unique=True, index=True)
    patient_id: int = Field(foreign_key="patients.id", index=True)
    examination_type_id: int = Field(foreign_key="examination_types.id")
    doctor_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    department: Optional[str] = Field(default=None, max_length=100)
    registration_date: date = Field(sa_column=Column(Date, nullable=False, index=True))
    registration_time: Optional[time] = Field(default=None, sa_column=Column(Time))
    scheduled_date: date = Field(sa_column=Column(Date, nullable=False, index=True))
    scheduled_time: Optional[time] = Field(default=None, sa_column=Column(Time))
    priority: str = Field(default='normal', max_length=20)
    registration_type: str = Field(default='normal', max_length=20)
    status: str = Field(default='unsigned', max_length=20, index=True)
    registration_fee: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric(10, 2)))
    payment_status: str = Field(default='unpaid', max_length=20)
    payment_method: Optional[str] = Field(default=None, max_length=20)
    chief_complaint: Optional[str] = Field(default=None, sa_column=Column(Text))
    present_illness: Optional[str] = Field(default=None, sa_column=Column(Text))
    referral_doctor: Optional[str] = Field(default=None, max_length=100)
    referral_hospital: Optional[str] = Field(default=None, max_length=200)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    check_in_time: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True), nullable=True))
    queue_number: Optional[int] = Field(default=None, sa_column=Column(Integer, index=True))
    estimated_wait_time: Optional[int] = Field(default=None, sa_column=Column(Integer))
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
        CheckConstraint("priority IN ('urgent', 'high', 'normal', 'low')", name='check_priority'),
        CheckConstraint("registration_type IN ('emergency', 'appointment', 'normal', 'followup')", name='check_registration_type'),
        CheckConstraint("status IN ('unsigned', 'checked_in', 'cancelled')", name='check_registration_status'),
        CheckConstraint("registration_fee >= 0", name='check_registration_fee'),
        CheckConstraint("payment_status IN ('unpaid', 'paid', 'refunded')", name='check_payment_status'),
        CheckConstraint("queue_number >= 0", name='check_queue_number'),
        CheckConstraint("estimated_wait_time >= 0", name='check_estimated_wait_time'),
    )
    
    def __repr__(self):
        return f"<Registration(id={self.id}, registration_number='{self.registration_number}')>"
