"""
眼底影像模型
"""
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, Boolean, BigInteger
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin, SoftDeleteMixin

class FundusImage(Base, TimestampMixin, SoftDeleteMixin):
    """眼底影像表:存储眼底检查产生的各种影像文件"""
    __tablename__ = 'fundus_images'

    id = Column(Integer, primary_key=True)
    examination_id = Column(Integer, ForeignKey('examinations.id', ondelete='CASCADE'), nullable=False)
    image_number = Column(String(50), nullable=False)
    eye_side = Column(Enum('OS', 'OD', name='eye_side'), nullable=False)
    capture_mode = Column(Enum('gray', 'color', name='capture_mode'), nullable=False)
    image_type = Column(String(50))
    image_position = Column(String(50))
    file_path = Column(String(500), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger)
    file_format = Column(String(20))
    image_quality = Column(Enum('excellent', 'good', 'fair', 'poor', name='image_quality'))
    resolution = Column(String(50))
    acquisition_device = Column(String(100))
    acquisition_parameters = Column(JSONB)
    thumbnail_data = Column(Text)
    is_primary = Column(Boolean, default=False)
    upload_status = Column(Enum('uploading', 'uploaded', 'failed', 'processing', name='upload_status'), default='uploaded')
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'))
    
    # 关系
    examination = relationship("Examination", back_populates="fundus_images")
    
    def __repr__(self):
        return f"<FundusImage(id={self.id}, image_number='{self.image_number}', eye_side='{self.eye_side}')>"