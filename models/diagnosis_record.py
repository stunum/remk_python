"""
诊断记录模型
"""
from datetime import datetime
from typing import Optional, List
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, CheckConstraint, DateTime, text, Boolean, ARRAY, String

class DiagnosisRecord(SQLModel, table=True):
    """诊断记录表:支持一次检查的多次诊断和诊断历史追踪"""
    __tablename__ = 'diagnosis_records'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    examination_id: int = Field(foreign_key="examinations.id", index=True)
    doctor_id: int = Field(foreign_key="users.id", index=True)
    diagnosis_type: str = Field(max_length=20)
    icd_code: Optional[str] = Field(default=None, max_length=20)
    diagnosis_name: str = Field(max_length=200)
    diagnosis_description: Optional[str] = Field(default=None, sa_column=Column(Text))
    severity: Optional[str] = Field(default=None, max_length=20)
    laterality: Optional[str] = Field(default=None, max_length=10)
    confidence_level: Optional[str] = Field(default=None, max_length=20)
    supporting_evidence: Optional[str] = Field(default=None, sa_column=Column(Text))
    differential_diagnoses: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    treatment_plan: Optional[str] = Field(default=None, sa_column=Column(Text))
    prognosis: Optional[str] = Field(default=None, sa_column=Column(Text))
    diagnosis_date: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
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
        CheckConstraint("diagnosis_type IN ('primary', 'secondary', 'differential', 'final')", name='check_diagnosis_type'),
        CheckConstraint("severity IN ('mild', 'moderate', 'severe')", name='check_severity'),
        CheckConstraint("laterality IN ('left', 'right', 'bilateral', 'unspecified')", name='check_laterality'),
        CheckConstraint("confidence_level IN ('definite', 'probable', 'possible', 'rule_out')", name='check_confidence_level'),
    )
    
    def __repr__(self):
        return f"<DiagnosisRecord(id={self.id}, examination_id={self.examination_id}, diagnosis='{self.diagnosis_name}')>"

