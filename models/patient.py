"""
患者模型
"""
from sqlalchemy import Column, Integer, String, Date, Text, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin, AuditMixin

class Patient(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """患者信息表:存储患者的基本信息和医疗背景"""
    __tablename__ = 'patients'

    id = Column(Integer, primary_key=True)
    patient_id = Column(String(50), nullable=False, unique=True)
    name = Column(String(100), nullable=False)
    gender = Column(Enum('male', 'female', 'other', name='gender_type'))
    birth_date = Column(Date)
    phone = Column(String(20))
    email = Column(String(100))
    address = Column(Text)
    emergency_contact = Column(String(100))
    emergency_phone = Column(String(20))
    medical_history = Column(Text)
    allergies = Column(Text)
    current_medications = Column(Text)
    insurance_info = Column(JSONB)
    status = Column(Enum('active', 'inactive', 'deceased', name='patient_status'), 
                   nullable=False, default='active')
    
    # 关系
    examinations = relationship("Examination", back_populates="patient")
    registrations = relationship("Registration", back_populates="patient")
    creator = relationship("User", foreign_keys=[AuditMixin.created_by], back_populates="created_patients")
    updater = relationship("User", foreign_keys=[AuditMixin.updated_by], back_populates="updated_patients")
    
    def __repr__(self):
        return f"<Patient(id={self.id}, patient_id='{self.patient_id}', name='{self.name}')>"