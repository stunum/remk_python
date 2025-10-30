"""
挂号登记模型
"""
from sqlalchemy import Column, Integer, String, Date, Time, Text, ForeignKey, Enum, Numeric, DateTime
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin, AuditMixin

class Registration(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """挂号表:管理患者挂号与预约流程"""
    __tablename__ = 'registrations'

    id = Column(Integer, primary_key=True)
    registration_number = Column(String(50), nullable=False, unique=True)
    patient_id = Column(Integer, ForeignKey('patients.id'), nullable=False)
    examination_type_id = Column(Integer, ForeignKey('examination_types.id'), nullable=False)
    doctor_id = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    examination_id = Column(Integer, ForeignKey('examinations.id', ondelete='SET NULL'), unique=True)
    department = Column(String(100))
    registration_date = Column(Date, nullable=False)
    registration_time = Column(Time)
    scheduled_date = Column(Date, nullable=False)
    scheduled_time = Column(Time)
    priority = Column(Enum('urgent', 'high', 'normal', 'low', name='priority_type'), default='normal')
    registration_type = Column(Enum('emergency', 'appointment', 'normal', 'followup', name='registration_type'), default='normal')
    status = Column(Enum('unsigned', 'checked_in', 'cancelled', name='registration_status'), nullable=False, default='unsigned')
    registration_fee = Column(Numeric(10, 2))
    payment_status = Column(Enum('unpaid', 'paid', 'refunded', name='payment_status'), default='unpaid')
    payment_method = Column(String(20))
    chief_complaint = Column(Text)
    present_illness = Column(Text)
    referral_doctor = Column(String(100))
    referral_hospital = Column(String(200))
    notes = Column(Text)
    check_in_time = Column(DateTime(timezone=True))
    queue_number = Column(Integer)
    estimated_wait_time = Column(Integer)
    
    # 关系
    patient = relationship("Patient", back_populates="registrations")
    examination_type = relationship("ExaminationType", back_populates="registrations")
    doctor = relationship("User", foreign_keys=[doctor_id], back_populates="doctor_registrations")
    examination = relationship("Examination", back_populates="registration")
    
    def __repr__(self):
        return f"<Registration(id={self.id}, registration_number='{self.registration_number}')>"