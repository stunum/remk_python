"""
系统日志模型
"""
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, Text, CheckConstraint, DateTime, text, Integer
from sqlalchemy.dialects.postgresql import JSONB, INET

class SystemLog(SQLModel, table=True):
    """系统日志表:记录系统操作和错误信息"""
    __tablename__ = 'system_logs'
    
    id: Optional[int] = Field(default=None, primary_key=True)
    log_level: str = Field(max_length=20)
    module: Optional[str] = Field(default=None, max_length=50)
    action: Optional[str] = Field(default=None, max_length=100)
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    ip_address: Optional[str] = Field(default=None, sa_column=Column(INET))
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text))
    request_id: Optional[str] = Field(default=None, max_length=100)
    session_id: Optional[str] = Field(default=None, max_length=100)
    resource_type: Optional[str] = Field(default=None, max_length=50)
    resource_id: Optional[str] = Field(default=None, max_length=100)
    operation_result: Optional[str] = Field(default=None, max_length=20)
    message: str = Field(sa_column=Column(Text, nullable=False))
    error_code: Optional[str] = Field(default=None, max_length=50)
    error_details: Optional[str] = Field(default=None, sa_column=Column(Text))
    execution_time_ms: Optional[int] = Field(default=None, sa_column=Column(Integer))
    additional_data: Optional[dict] = Field(default=None, sa_column=Column(JSONB))
    created_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), server_default=text('CURRENT_TIMESTAMP'), index=True)
    )
    
    __table_args__ = (
        CheckConstraint("log_level IN ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')", name='check_log_level'),
        CheckConstraint("operation_result IN ('success', 'failure', 'partial')", name='check_operation_result'),
    )
    
    def __repr__(self):
        return f"<SystemLog(id={self.id}, level='{self.log_level}', module='{self.module}', action='{self.action}')>"

