"""
用户/医生信息管理模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, DateTime, CheckConstraint, text

class User(SQLModel, table=True):
    """用户信息表:管理系统中所有用户(医生、技师、管理员等)的基本信息"""
    __tablename__ = 'users'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(max_length=50, unique=True, index=True)
    password_hash: str = Field(max_length=255)
    email: Optional[str] = Field(default=None, max_length=100, unique=True)
    phone: Optional[str] = Field(default=None, max_length=20)
    full_name: str = Field(max_length=100)
    user_type: str = Field(default='doctor', max_length=20)
    department: Optional[str] = Field(default=None, max_length=100, index=True)
    title: Optional[str] = Field(default=None, max_length=50)
    license_number: Optional[str] = Field(default=None, max_length=50)
    status: str = Field(default='active', max_length=20, index=True)
    last_login_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
    deleted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True)
    )
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
        CheckConstraint("user_type IN ('admin', 'doctor', 'technician', 'viewer')", name='check_user_type'),
        CheckConstraint("status IN ('active', 'inactive', 'locked')", name='check_status'),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', full_name='{self.full_name}')>"
