"""
检查记录模型
"""
from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin, AuditMixin

class Examination(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """检查记录表:记录每次眼底检查的基本信息和结果"""
    __tablename__ = 'examinations'

    id = Column(Integer, primary_key=True)
    examination_number = Column(String(50), nullable=False, unique=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    examination_type_id = Column(Integer, ForeignKey('examination_types.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    technician_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    examination_date = Column(Date, nullable=False)
    examination_time = Column(Time)
    eye_side = Column(Enum('left', 'right', 'both', name='eye_side_type'))
    chief_complaint = Column(Text)
    present_illness = Column(Text)
    examination_findings = Column(Text)
    preliminary_diagnosis = Column(Text)
    recommendations = Column(Text)
    follow_up_date = Column(Date)
    status = Column(Enum('pending', 'in_progress', 'completed', 'cancelled', name='examination_status'), 
                   nullable=False, default='pending')
    notes = Column(Text)
    
    # 关系
    patient = relationship("Patient", back_populates="examinations")
    examination_type = relationship("ExaminationType", back_populates="examinations")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_examinations")
    technician = relationship("User", foreign_keys=[technician_id], back_populates="technician_examinations")
    registration = relationship("Registration", back_populates="examination", uselist=False)
    fundus_images = relationship("FundusImage", back_populates="examination", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Examination(id={self.id}, examination_number='{self.examination_number}')>"