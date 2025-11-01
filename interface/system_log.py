"""
系统日志查询API - RESTful风格
注意：系统日志通常只提供查询功能，不提供创建、更新、删除接口
"""
from typing import Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel

from models.system_log import SystemLog
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log
from datetime import timedelta

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class SystemLogResponse(BaseModel):
    """系统日志响应模型"""
    id: int
    log_level: str
    module: Optional[str] = None
    action: Optional[str] = None
    user_id: Optional[int] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    session_id: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    operation_result: Optional[str] = None
    message: str
    error_code: Optional[str] = None
    error_details: Optional[str] = None
    execution_time_ms: Optional[int] = None
    additional_data: Optional[dict] = None
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ==================== API 端点 ====================

@router.get("/{log_id}", response_model=ResponseModel, summary="根据ID获取单条日志")
def get_system_log(log_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单条系统日志
    
    - **log_id**: 日志ID
    """
    log.debug(f"查询系统日志: id={log_id}")
    
    system_log = db.query(SystemLog).filter(SystemLog.id == log_id).first()
    
    if not system_log:
        log.warning(f"系统日志未找到: id={log_id}")
        return error_response(code=404, msg="系统日志未找到")
    
    log_response = SystemLogResponse.model_validate(system_log)
    return success_response(data=log_response.model_dump())


@router.get("/", response_model=ResponseModel, summary="查询系统日志列表")
def list_system_logs(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    log_level: Optional[str] = Query(None, description="日志级别筛选 (DEBUG/INFO/WARN/ERROR/FATAL)"),
    module: Optional[str] = Query(None, description="模块名称筛选"),
    action: Optional[str] = Query(None, description="操作名称筛选"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    resource_type: Optional[str] = Query(None, description="资源类型筛选"),
    operation_result: Optional[str] = Query(None, description="操作结果筛选 (success/failure/partial)"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    message_keyword: Optional[str] = Query(None, description="消息关键词搜索"),
    db: Session = Depends(get_db)
):
    """
    查询系统日志列表（支持分页和多条件筛选）
    
    支持的筛选条件：
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **log_level**: 日志级别
    - **module**: 模块名称
    - **action**: 操作名称
    - **user_id**: 用户ID
    - **resource_type**: 资源类型
    - **operation_result**: 操作结果
    - **start_date**: 开始日期
    - **end_date**: 结束日期
    - **message_keyword**: 消息关键词
    """
    log.debug(f"分页查询系统日志: page={page}, page_size={page_size}")
    
    offset = (page - 1) * page_size
    
    # 构建查询
    query = db.query(SystemLog)
    
    # 添加筛选条件
    if log_level:
        query = query.filter(SystemLog.log_level == log_level)
    if module:
        query = query.filter(SystemLog.module == module)
    if action:
        query = query.filter(SystemLog.action == action)
    if user_id is not None:
        query = query.filter(SystemLog.user_id == user_id)
    if resource_type:
        query = query.filter(SystemLog.resource_type == resource_type)
    if operation_result:
        query = query.filter(SystemLog.operation_result == operation_result)
    if start_date:
        query = query.filter(SystemLog.created_at >= start_date)
    if end_date:
        # 结束日期包含当天的所有时间
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(SystemLog.created_at <= end_datetime)
    if message_keyword:
        query = query.filter(SystemLog.message.like(f"%{message_keyword}%"))
    
    # 获取总数和分页数据
    total = query.count()
    system_logs = query.order_by(SystemLog.created_at.desc()).offset(offset).limit(page_size).all()
    
    log.debug(f"查询到 {total} 条系统日志，当前页 {len(system_logs)} 条")
    
    # 转换为响应模型列表
    logs_response = [SystemLogResponse.model_validate(sys_log).model_dump() for sys_log in system_logs]
    
    return success_response(data={
        "logs": logs_response,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    })


@router.get("/stats/summary", response_model=ResponseModel, summary="获取日志统计摘要")
def get_log_statistics(
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    db: Session = Depends(get_db)
):
    """
    获取系统日志统计摘要
    
    - **start_date**: 开始日期（可选）
    - **end_date**: 结束日期（可选）
    
    返回各级别日志的数量统计和操作结果统计
    """
    log.debug(f"获取日志统计: start_date={start_date}, end_date={end_date}")
    
    # 构建基础查询
    query = db.query(SystemLog)
    
    if start_date:
        query = query.filter(SystemLog.created_at >= start_date)
    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(SystemLog.created_at <= end_datetime)
    
    # 统计总数
    total_logs = query.count()
    
    # 按日志级别统计
    level_stats = {}
    for level in ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']:
        count = query.filter(SystemLog.log_level == level).count()
        level_stats[level] = count
    
    # 按操作结果统计
    result_stats = {}
    for result in ['success', 'failure', 'partial']:
        count = query.filter(SystemLog.operation_result == result).count()
        result_stats[result] = count
    
    # 按模块统计（Top 10）
    module_stats_raw = db.query(
        SystemLog.module,
        db.func.count(SystemLog.id).label('count')
    ).filter(
        SystemLog.module.isnot(None)
    ).group_by(
        SystemLog.module
    ).order_by(
        db.func.count(SystemLog.id).desc()
    ).limit(10).all()
    
    module_stats = {module: count for module, count in module_stats_raw if module}
    
    log.debug(f"日志统计完成: total={total_logs}")
    
    return success_response(data={
        "total_logs": total_logs,
        "level_statistics": level_stats,
        "result_statistics": result_stats,
        "top_modules": module_stats,
        "date_range": {
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None
        }
    })


@router.delete("/cleanup", response_model=ResponseModel, summary="清理旧日志（管理员功能）")
def cleanup_old_logs(
    days: int = Query(30, ge=1, le=365, description="保留最近多少天的日志"),
    db: Session = Depends(get_db)
):
    """
    清理旧日志（物理删除）
    
    - **days**: 保留最近多少天的日志（1-365天）
    
    注意：这是物理删除操作，请谨慎使用
    """
    log.warning(f"开始清理 {days} 天前的旧日志")
    
    # 计算截止日期
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # 查询要删除的日志
    old_logs = db.query(SystemLog).filter(SystemLog.created_at < cutoff_date).all()
    
    if not old_logs:
        log.info("没有需要清理的旧日志")
        return success_response(data={
            "deleted_count": 0,
            "cutoff_date": cutoff_date.isoformat()
        })
    
    # 执行删除
    deleted_count = len(old_logs)
    for old_log in old_logs:
        db.delete(old_log)
    
    db.commit()
    log.warning(f"成功清理 {deleted_count} 条旧日志，截止日期: {cutoff_date}")
    
    return success_response(data={
        "deleted_count": deleted_count,
        "cutoff_date": cutoff_date.isoformat()
    })




