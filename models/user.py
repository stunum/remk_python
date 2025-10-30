"""
用户模型
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin, AuditMixin

class User(Base, TimestampMixin, SoftDeleteMixin):
    """用户信息表:管理系统中所有用户(医生、技师、管理员等)的基本信息"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(20))
    full_name = Column(String(100), nullable=False)
    user_type = Column(Enum('admin', 'doctor', 'technician', 'viewer', name='user_type'), 
                      nullable=False, default='doctor')
    department = Column(String(100))
    title = Column(String(50))
    license_number = Column(String(50))
    status = Column(Enum('active', 'inactive', 'locked', name='user_status'), 
                   nullable=False, default='active')
    last_login_at = Column(DateTime(timezone=True))
    
    # 关系
    created_patients = relationship("Patient", foreign_keys="Patient.created_by", back_populates="creator")
    updated_patients = relationship("Patient", foreign_keys="Patient.updated_by", back_populates="updater")
    
    doctor_examinations = relationship("Examination", foreign_keys="Examination.doctor_id", back_populates="doctor")
    technician_examinations = relationship("Examination", foreign_keys="Examination.technician_id", back_populates="technician")
    
    doctor_registrations = relationship("Registration", foreign_keys="Registration.doctor_id", back_populates="doctor")
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', full_name='{self.full_name}')>"