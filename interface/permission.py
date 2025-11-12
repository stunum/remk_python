"""
权限管理API - RESTful风格
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField

from models.permission import Permission
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log
from utils.jwt_auth import get_current_user_info, require_permission

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class PermissionCreate(BaseModel):
    """权限创建模型"""
    permission_name: str = PydanticField(..., min_length=1, max_length=100, description="权限名称")
    permission_code: str = PydanticField(..., min_length=1, max_length=50, description="权限代码")
    resource: str = PydanticField(..., min_length=1, max_length=50, description="资源名称")
    action: str = PydanticField(..., min_length=1, max_length=50, description="操作类型")
    description: Optional[str] = PydanticField(None, description="权限描述")
    is_active: bool = PydanticField(default=True, description="是否启用")


class PermissionUpdate(BaseModel):
    """权限更新模型"""
    permission_name: Optional[str] = PydanticField(None, min_length=1, max_length=100, description="权限名称")
    resource: Optional[str] = PydanticField(None, min_length=1, max_length=50, description="资源名称")
    action: Optional[str] = PydanticField(None, min_length=1, max_length=50, description="操作类型")
    description: Optional[str] = PydanticField(None, description="权限描述")
    is_active: Optional[bool] = PydanticField(None, description="是否启用")


class PermissionResponse(BaseModel):
    """权限响应模型"""
    id: int
    permission_name: str
    permission_code: str
    resource: str
    action: str
    description: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PermissionDeleteRequest(BaseModel):
    """批量删除权限请求模型"""
    permission_ids: List[int] = PydanticField(..., min_length=1, description="要删除的权限ID列表")


# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建新权限", dependencies=[Depends(get_current_user_info), Depends(require_permission('PERMISSION_MANAGE'))])
def create_permission(permission_data: PermissionCreate, db: Session = Depends(get_db)):
    """
    创建新权限
    
    - **permission_name**: 权限名称（唯一）
    - **permission_code**: 权限代码（唯一）
    - **resource**: 资源名称
    - **action**: 操作类型（如：create, read, update, delete）
    - **description**: 权限描述
    - **is_active**: 是否启用
    """
    log.info(f"创建新权限: permission_name={permission_data.permission_name}")
    
    # 检查权限名称是否已存在
    existing_name = db.query(Permission).filter(
        Permission.permission_name == permission_data.permission_name,
        Permission.deleted_at.is_(None)
    ).first()
    if existing_name:
        log.warning(f"权限名称已存在: {permission_data.permission_name}")
        return error_response(code=400, msg="权限名称已存在")
    
    # 检查权限代码是否已存在
    existing_code = db.query(Permission).filter(
        Permission.permission_code == permission_data.permission_code,
        Permission.deleted_at.is_(None)
    ).first()
    if existing_code:
        log.warning(f"权限代码已存在: {permission_data.permission_code}")
        return error_response(code=400, msg="权限代码已存在")
    
    # 创建权限对象
    new_permission = Permission(**permission_data.model_dump())
    db.add(new_permission)
    db.commit()
    db.refresh(new_permission)
    
    log.info(f"成功创建权限: id={new_permission.id}, permission_name={new_permission.permission_name}")
    
    permission_response = PermissionResponse.model_validate(new_permission)
    return success_response(data=permission_response.model_dump())


@router.get("/{permission_id}", response_model=ResponseModel, summary="根据ID获取单个权限", dependencies=[Depends(get_current_user_info), Depends(require_permission('PERMISSION_MANAGE'))])
def get_permission(permission_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个权限信息（排除已软删除的权限）
    
    - **permission_id**: 权限ID
    """
    log.debug(f"查询权限: id={permission_id}")
    
    permission = db.query(Permission).filter(
        Permission.id == permission_id,
        Permission.deleted_at.is_(None)
    ).first()
    
    if not permission:
        log.warning(f"权限未找到: id={permission_id}")
        return error_response(code=404, msg="权限未找到")
    
    log.debug(f"成功查询权限: id={permission.id}, permission_name={permission.permission_name}")
    
    permission_response = PermissionResponse.model_validate(permission)
    return success_response(data=permission_response.model_dump())


@router.get("/", response_model=ResponseModel, summary="查询权限列表", dependencies=[Depends(get_current_user_info), Depends(require_permission('PERMISSION_MANAGE'))])
def list_permissions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用筛选"),
    resource: Optional[str] = Query(None, description="资源名称筛选"),
    action: Optional[str] = Query(None, description="操作类型筛选"),
    permission_name: Optional[str] = Query(None, description="权限名称模糊查询"),
    db: Session = Depends(get_db)
):
    """
    查询权限列表（支持分页和筛选）
    
    支持的筛选条件：
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **is_active**: 是否启用
    - **resource**: 资源名称
    - **action**: 操作类型
    - **permission_name**: 权限名称模糊查询
    """
    log.debug(f"分页查询权限: page={page}, page_size={page_size}")
    
    offset = (page - 1) * page_size
    
    # 构建查询用于计算总数，排除软删除的权限
    count_query = db.query(Permission).filter(Permission.deleted_at.is_(None))
    
    # 添加筛选条件
    if is_active is not None:
        count_query = count_query.filter(Permission.is_active == is_active)
    if resource:
        count_query = count_query.filter(Permission.resource == resource)
    if action:
        count_query = count_query.filter(Permission.action == action)
    if permission_name:
        count_query = count_query.filter(Permission.permission_name.like(f"%{permission_name}%"))
    
    # 获取总数
    total = count_query.count()
    
    # 重新构建查询用于获取分页数据
    data_query = db.query(Permission).filter(Permission.deleted_at.is_(None))
    
    # 添加筛选条件
    if is_active is not None:
        data_query = data_query.filter(Permission.is_active == is_active)
    if resource:
        data_query = data_query.filter(Permission.resource == resource)
    if action:
        data_query = data_query.filter(Permission.action == action)
    if permission_name:
        data_query = data_query.filter(Permission.permission_name.like(f"%{permission_name}%"))
    
    # 获取分页数据
    permissions = data_query.order_by(Permission.resource, Permission.action).offset(offset).limit(page_size).all()
    
    log.debug(f"查询到 {total} 个权限，当前页 {len(permissions)} 个")
    
    # 转换为响应模型列表
    permissions_response = [PermissionResponse.model_validate(perm).model_dump() for perm in permissions]
    
    return success_response(data={
        "permissions": permissions_response,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    })


@router.put("/{permission_id}", response_model=ResponseModel, summary="更新权限信息", dependencies=[Depends(get_current_user_info), Depends(require_permission('PERMISSION_MANAGE'))])
def update_permission(permission_id: int, permission_data: PermissionUpdate, db: Session = Depends(get_db)):
    """
    更新权限信息（排除已软删除的权限）
    
    - **permission_id**: 权限ID
    - 只更新提供的字段，未提供的字段保持不变
    - permission_code 不可修改
    """
    log.info(f"更新权限信息: id={permission_id}")
    
    # 查找权限（排除软删除）
    permission = db.query(Permission).filter(
        Permission.id == permission_id,
        Permission.deleted_at.is_(None)
    ).first()
    
    if not permission:
        log.warning(f"权限未找到: id={permission_id}")
        return error_response(code=404, msg="权限未找到")
    
    # 检查权限名称是否被其他权限使用
    if permission_data.permission_name and permission_data.permission_name != permission.permission_name:
        existing_name = db.query(Permission).filter(
            Permission.permission_name == permission_data.permission_name,
            Permission.id != permission_id,
            Permission.deleted_at.is_(None)
        ).first()
        if existing_name:
            log.warning(f"权限名称已被使用: {permission_data.permission_name}")
            return error_response(code=400, msg="权限名称已被其他权限使用")
    
    # 更新字段（只更新提供的字段）
    update_data = permission_data.model_dump(exclude_unset=True)
    if not update_data:
        log.warning(f"没有提供任何更新字段: id={permission_id}")
        return error_response(code=400, msg="没有提供任何更新字段")
    
    for key, value in update_data.items():
        setattr(permission, key, value)
    
    db.commit()
    db.refresh(permission)
    
    log.info(f"成功更新权限: id={permission.id}, permission_name={permission.permission_name}")
    
    permission_response = PermissionResponse.model_validate(permission)
    return success_response(data=permission_response.model_dump())


@router.delete("/{permission_id}", response_model=ResponseModel, summary="删除单个权限（软删除）", dependencies=[Depends(get_current_user_info), Depends(require_permission('PERMISSION_MANAGE'))])
def delete_permission(permission_id: int, db: Session = Depends(get_db)):
    """
    删除单个权限（软删除）
    
    - **permission_id**: 权限ID
    """
    log.info(f"删除权限: id={permission_id}")
    
    permission = db.query(Permission).filter(
        Permission.id == permission_id,
        Permission.deleted_at.is_(None)
    ).first()
    
    if not permission:
        log.warning(f"权限未找到: id={permission_id}")
        return error_response(code=404, msg="权限未找到")
    
    # 执行软删除
    permission.deleted_at = datetime.now()
    db.commit()
    
    log.info(f"成功删除权限: id={permission.id}, permission_name={permission.permission_name}")
    
    return success_response(data={"deleted_id": permission_id})


@router.delete("/", response_model=ResponseModel, summary="批量删除权限（软删除）", dependencies=[Depends(get_current_user_info), Depends(require_permission('PERMISSION_MANAGE'))])
def delete_permissions(delete_request: PermissionDeleteRequest, db: Session = Depends(get_db)):
    """
    批量软删除权限
    
    - **permission_ids**: 要删除的权限ID列表
    """
    log.info(f"批量删除权限: ids={delete_request.permission_ids}")
    
    # 查找未被软删除的权限
    permissions = db.query(Permission).filter(
        Permission.id.in_(delete_request.permission_ids),
        Permission.deleted_at.is_(None)
    ).all()
    
    if not permissions:
        log.warning(f"未找到可删除的权限: {delete_request.permission_ids}")
        return error_response(code=404, msg="未找到可删除的权限")
    
    # 执行软删除
    deleted_count = 0
    deleted_ids = []
    
    for permission in permissions:
        permission.deleted_at = datetime.now()
        deleted_count += 1
        deleted_ids.append(permission.id)
    
    db.commit()
    log.info(f"成功软删除 {deleted_count} 个权限: {deleted_ids}")
    
    return success_response(data={
        "deleted_count": deleted_count,
        "deleted_ids": deleted_ids
    })
