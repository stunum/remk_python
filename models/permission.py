"""
权限管理模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, CheckConstraint, DateTime, text, Boolean

class Permission(SQLModel, table=True):
    """权限表:定义系统中的各种权限"""
    __tablename__ = 'permissions'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    permission_name: str = Field(max_length=100, unique=True, index=True)
    permission_code: str = Field(max_length=50, unique=True, index=True)
    resource: str = Field(max_length=50)
    action: str = Field(max_length=50)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    
    def __repr__(self):
        return f"<Permission(id={self.id}, permission_name='{self.permission_name}', resource='{self.resource}', action='{self.action}')>"

