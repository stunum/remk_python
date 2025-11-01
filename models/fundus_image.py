"""
眼底影像管理模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, Boolean, BigInteger, CheckConstraint, DateTime, text
from sqlalchemy.dialects.postgresql import JSONB

class FundusImage(SQLModel, table=True):
    """眼底影像表:存储眼底检查产生的各种影像文件"""
    __tablename__ = 'fundus_images'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    examination_id: int = Field(foreign_key="examinations.id", index=True)
    image_number: str = Field(max_length=50)
    eye_side: str = Field(max_length=10)
    capture_mode: str = Field(max_length=20)
    image_type: Optional[str] = Field(default=None, max_length=50)
    image_position: Optional[str] = Field(default=None, max_length=50)
    file_path: str = Field(max_length=500)
    file_name: str = Field(max_length=255)
    file_size: Optional[int] = Field(default=None, sa_column=Column(BigInteger))
    file_format: Optional[str] = Field(default=None, max_length=20)
    image_quality: Optional[str] = Field(default=None, max_length=20)
    resolution: Optional[str] = Field(default=None, max_length=50)
    acquisition_device: Optional[str] = Field(default=None, max_length=100)
    acquisition_parameters: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    thumbnail_data: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_primary: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    upload_status: str = Field(default='uploaded', max_length=20)
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
    
    __table_args__ = (
        CheckConstraint("eye_side IN ('OS', 'OD')", name='check_fundus_eye_side'),
        CheckConstraint("capture_mode IN ('gray', 'color')", name='check_capture_mode'),
        CheckConstraint("file_size >= 0", name='check_file_size'),
        CheckConstraint("image_quality IN ('excellent', 'good', 'fair', 'poor')", name='check_image_quality'),
        CheckConstraint("upload_status IN ('uploading', 'uploaded', 'failed', 'processing')", name='check_upload_status'),
    )
    
    def __repr__(self):
        return f"<FundusImage(id={self.id}, image_number='{self.image_number}', eye_side='{self.eye_side}')>"
