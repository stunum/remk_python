"""
用户角色关联模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, CheckConstraint, DateTime, text, Boolean, UniqueConstraint

class UserRole(SQLModel, table=True):
    """用户角色关联表:管理用户与角色的关系"""
    __tablename__ = 'user_roles'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    role_id: int = Field(foreign_key="roles.id", index=True)
    assigned_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    assigned_by: Optional[int] = Field(default=None, foreign_key="users.id")
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    
    __table_args__ = (
        UniqueConstraint('user_id', 'role_id', name='uq_user_role'),
    )
    
    def __repr__(self):
        return f"<UserRole(id={self.id}, user_id={self.user_id}, role_id={self.role_id})>"

