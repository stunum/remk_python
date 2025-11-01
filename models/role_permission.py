"""
角色权限关联模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, CheckConstraint, DateTime, text, Boolean, UniqueConstraint

class RolePermission(SQLModel, table=True):
    """角色权限关联表:管理角色与权限的关系"""
    __tablename__ = 'role_permissions'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    role_id: int = Field(foreign_key="roles.id", index=True)
    permission_id: int = Field(foreign_key="permissions.id", index=True)
    granted_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'))
    )
    granted_by: Optional[int] = Field(default=None, foreign_key="users.id")
    is_active: bool = Field(default=True, sa_column=Column(Boolean, default=True))
    deleted_at: Optional[datetime] = Field(default=None, sa_column=Column(DateTime(timezone=True)))
    
    __table_args__ = (
        UniqueConstraint('role_id', 'permission_id', name='uq_role_permission'),
    )
    
    def __repr__(self):
        return f"<RolePermission(id={self.id}, role_id={self.role_id}, permission_id={self.permission_id})>"

