"""
基础模型类，提供共享功能
"""
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey, func
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TimestampMixin:
    """时间戳混入类，提供创建和更新时间"""
    created_at = Column(DateTime(timezone=True), default=func.now())
    updated_at = Column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

class SoftDeleteMixin:
    """软删除混入类"""
    deleted_at = Column(DateTime(timezone=True), nullable=True)

class AuditMixin:
    """审计混入类，记录创建和更新用户"""
    created_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    updated_by = Column(Integer, ForeignKey('users.id', ondelete='SET NULL'), nullable=True)