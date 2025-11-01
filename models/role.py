"""
角色管理模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, CheckConstraint, DateTime, text, Boolean

class Role(SQLModel, table=True):
    """角色表:定义系统中的各种角色"""
    __tablename__ = 'roles'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    role_name: str = Field(max_length=50, unique=True, index=True)
    role_code: str = Field(max_length=20, unique=True, index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_system_role: bool = Field(default=False, sa_column=Column(Boolean, default=False))
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    
    def __repr__(self):
        return f"<Role(id={self.id}, role_name='{self.role_name}', role_code='{self.role_code}')>"

