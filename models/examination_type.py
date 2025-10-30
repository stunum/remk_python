"""
检查类型模型
"""
from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin

class ExaminationType(Base, TimestampMixin, SoftDeleteMixin):
    """检查类型表:定义不同类型的眼底检查项目"""
    __tablename__ = 'examination_types'

    id = Column(Integer, primary_key=True)
    type_code = Column(String(20), nullable=False, unique=True)
    type_name = Column(String(100), nullable=False)
    description = Column(Text)
    body_part = Column(String(50))
    duration_minutes = Column(Integer)
    preparation_instructions = Column(Text)
    is_active = Column(Boolean, default=True)
    
    # 关系
    examinations = relationship("Examination", back_populates="examination_type")
    registrations = relationship("Registration", back_populates="examination_type")
    
    def __repr__(self):
        return f"<ExaminationType(id={self.id}, type_code='{self.type_code}', type_name='{self.type_name}')>"