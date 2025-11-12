"""
角色权限关联管理API - RESTful风格
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField

from models.role_permission import RolePermission
from models.role import Role
from models.permission import Permission
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log
from utils.jwt_auth import get_current_user_info, require_permission

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class RolePermissionCreate(BaseModel):
    """角色权限关联创建模型"""
    role_id: int = PydanticField(..., description="角色ID")
    permission_id: int = PydanticField(..., description="权限ID")
    granted_by: Optional[int] = PydanticField(None, description="授权人ID")
    is_active: bool = PydanticField(default=True, description="是否有效")


class RolePermissionUpdate(BaseModel):
    """角色权限关联更新模型"""
    is_active: Optional[bool] = PydanticField(None, description="是否有效")


class RolePermissionResponse(BaseModel):
    """角色权限关联响应模型"""
    id: int
    role_id: int
    permission_id: int
    granted_at: Optional[datetime] = None
    granted_by: Optional[int] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class RolePermissionDetailResponse(BaseModel):
    """角色权限关联详细响应模型（包含角色和权限信息）"""
    id: int
    role_id: int
    role_name: Optional[str] = None
    role_code: Optional[str] = None
    permission_id: int
    permission_name: Optional[str] = None
    permission_code: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[str] = None
    granted_at: Optional[datetime] = None
    granted_by: Optional[int] = None
    is_active: bool


class RolePermissionDeleteRequest(BaseModel):
    """批量删除角色权限关联请求模型"""
    role_permission_ids: List[int] = PydanticField(..., min_length=1, description="要删除的角色权限关联ID列表")


# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建角色权限关联", dependencies=[Depends(get_current_user_info), Depends(require_permission('ROLE_PERMISSION_ASSIGN'))])
def create_role_permission(role_permission_data: RolePermissionCreate, db: Session = Depends(get_db)):
    """
    创建角色权限关联
    
    - **role_id**: 角色ID
    - **permission_id**: 权限ID
    - **granted_by**: 授权人ID
    - **is_active**: 是否有效
    """
    log.info(f"创建角色权限关联: role_id={role_permission_data.role_id}, permission_id={role_permission_data.permission_id}")
    
    # 检查角色是否存在
    role = db.query(Role).filter(Role.id == role_permission_data.role_id, Role.deleted_at.is_(None)).first()
    if not role:
        log.warning(f"角色不存在: role_id={role_permission_data.role_id}")
        return error_response(code=404, msg="角色不存在")
    
    # 检查权限是否存在
    permission = db.query(Permission).filter(Permission.id == role_permission_data.permission_id, Permission.deleted_at.is_(None)).first()
    if not permission:
        log.warning(f"权限不存在: permission_id={role_permission_data.permission_id}")
        return error_response(code=404, msg="权限不存在")
    
    # 检查关联是否已存在
    existing = db.query(RolePermission).filter(
        RolePermission.role_id == role_permission_data.role_id,
        RolePermission.permission_id == role_permission_data.permission_id,
        RolePermission.deleted_at.is_(None)
    ).first()
    if existing:
        log.warning(f"角色权限关联已存在: role_id={role_permission_data.role_id}, permission_id={role_permission_data.permission_id}")
        return error_response(code=400, msg="角色权限关联已存在")
    
    # 创建角色权限关联
    new_role_permission = RolePermission(**role_permission_data.model_dump())
    db.add(new_role_permission)
    db.commit()
    db.refresh(new_role_permission)
    
    log.info(f"成功创建角色权限关联: id={new_role_permission.id}")
    
    role_permission_response = RolePermissionResponse.model_validate(new_role_permission)
    return success_response(data=role_permission_response.model_dump())


@router.get("/{role_permission_id}", response_model=ResponseModel, summary="根据ID获取角色权限关联", dependencies=[Depends(get_current_user_info), Depends(require_permission('ROLE_PERMISSION_ASSIGN'))])
def get_role_permission(role_permission_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取角色权限关联信息（排除已软删除的关联）
    
    - **role_permission_id**: 角色权限关联ID
    """
    log.debug(f"查询角色权限关联: id={role_permission_id}")
    
    role_permission = db.query(RolePermission).filter(
        RolePermission.id == role_permission_id,
        RolePermission.deleted_at.is_(None)
    ).first()
    
    if not role_permission:
        log.warning(f"角色权限关联未找到: id={role_permission_id}")
        return error_response(code=404, msg="角色权限关联未找到")
    
    # 获取关联的角色和权限信息
    role = db.query(Role).filter(Role.id == role_permission.role_id).first()
    permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
    
    detail_response = RolePermissionDetailResponse(
        id=role_permission.id,
        role_id=role_permission.role_id,
        role_name=role.role_name if role else None,
        role_code=role.role_code if role else None,
        permission_id=role_permission.permission_id,
        permission_name=permission.permission_name if permission else None,
        permission_code=permission.permission_code if permission else None,
        resource=permission.resource if permission else None,
        action=permission.action if permission else None,
        granted_at=role_permission.granted_at,
        granted_by=role_permission.granted_by,
        is_active=role_permission.is_active
    )
    
    return success_response(data=detail_response.model_dump())


@router.get("/", response_model=ResponseModel, summary="查询角色权限关联列表", dependencies=[Depends(get_current_user_info), Depends(require_permission('ROLE_PERMISSION_ASSIGN'))])
def list_role_permissions(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    role_id: Optional[int] = Query(None, description="角色ID筛选"),
    permission_id: Optional[int] = Query(None, description="权限ID筛选"),
    is_active: Optional[bool] = Query(None, description="是否有效筛选"),
    db: Session = Depends(get_db)
):
    """
    查询角色权限关联列表（支持分页和筛选）
    
    支持的筛选条件：
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **role_id**: 角色ID
    - **permission_id**: 权限ID
    - **is_active**: 是否有效
    """
    log.debug(f"分页查询角色权限关联: page={page}, page_size={page_size}")
    
    offset = (page - 1) * page_size
    
    # 构建查询用于计算总数，排除软删除的关联
    count_query = db.query(RolePermission).filter(RolePermission.deleted_at.is_(None))
    
    # 添加筛选条件
    if role_id is not None:
        count_query = count_query.filter(RolePermission.role_id == role_id)
    if permission_id is not None:
        count_query = count_query.filter(RolePermission.permission_id == permission_id)
    if is_active is not None:
        count_query = count_query.filter(RolePermission.is_active == is_active)
    
    # 获取总数
    total = count_query.count()
    
    # 重新构建查询用于获取分页数据
    data_query = db.query(RolePermission).filter(RolePermission.deleted_at.is_(None))
    
    # 添加筛选条件
    if role_id is not None:
        data_query = data_query.filter(RolePermission.role_id == role_id)
    if permission_id is not None:
        data_query = data_query.filter(RolePermission.permission_id == permission_id)
    if is_active is not None:
        data_query = data_query.filter(RolePermission.is_active == is_active)
    
    # 获取分页数据
    role_permissions = data_query.order_by(RolePermission.granted_at.desc()).offset(offset).limit(page_size).all()
    
    log.debug(f"查询到 {total} 个角色权限关联，当前页 {len(role_permissions)} 个")
    
    # 转换为详细响应模型列表
    role_permissions_response = []
    for role_permission in role_permissions:
        role = db.query(Role).filter(Role.id == role_permission.role_id).first()
        permission = db.query(Permission).filter(Permission.id == role_permission.permission_id).first()
        
        detail_response = RolePermissionDetailResponse(
            id=role_permission.id,
            role_id=role_permission.role_id,
            role_name=role.role_name if role else None,
            role_code=role.role_code if role else None,
            permission_id=role_permission.permission_id,
            permission_name=permission.permission_name if permission else None,
            permission_code=permission.permission_code if permission else None,
            resource=permission.resource if permission else None,
            action=permission.action if permission else None,
            granted_at=role_permission.granted_at,
            granted_by=role_permission.granted_by,
            is_active=role_permission.is_active
        )
        role_permissions_response.append(detail_response.model_dump())
    
    return success_response(data={
        "role_permissions": role_permissions_response,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    })


@router.put("/{role_permission_id}", response_model=ResponseModel, summary="更新角色权限关联", dependencies=[Depends(get_current_user_info), Depends(require_permission('ROLE_PERMISSION_ASSIGN'))])
def update_role_permission(role_permission_id: int, role_permission_data: RolePermissionUpdate, db: Session = Depends(get_db)):
    """
    更新角色权限关联（排除已软删除的关联）
    
    - **role_permission_id**: 角色权限关联ID
    - 只更新提供的字段，未提供的字段保持不变
    """
    log.info(f"更新角色权限关联: id={role_permission_id}")
    
    # 查找角色权限关联（排除软删除）
    role_permission = db.query(RolePermission).filter(
        RolePermission.id == role_permission_id,
        RolePermission.deleted_at.is_(None)
    ).first()
    
    if not role_permission:
        log.warning(f"角色权限关联未找到: id={role_permission_id}")
        return error_response(code=404, msg="角色权限关联未找到")
    
    # 更新字段（只更新提供的字段）
    update_data = role_permission_data.model_dump(exclude_unset=True)
    if not update_data:
        log.warning(f"没有提供任何更新字段: id={role_permission_id}")
        return error_response(code=400, msg="没有提供任何更新字段")
    
    for key, value in update_data.items():
        setattr(role_permission, key, value)
    
    db.commit()
    db.refresh(role_permission)
    
    log.info(f"成功更新角色权限关联: id={role_permission.id}")
    
    role_permission_response = RolePermissionResponse.model_validate(role_permission)
    return success_response(data=role_permission_response.model_dump())


@router.delete("/{role_permission_id}", response_model=ResponseModel, summary="删除角色权限关联（软删除）", dependencies=[Depends(get_current_user_info), Depends(require_permission('ROLE_PERMISSION_ASSIGN'))])
def delete_role_permission(role_permission_id: int, db: Session = Depends(get_db)):
    """
    删除角色权限关联（软删除）
    
    - **role_permission_id**: 角色权限关联ID
    """
    log.info(f"删除角色权限关联: id={role_permission_id}")
    
    role_permission = db.query(RolePermission).filter(
        RolePermission.id == role_permission_id,
        RolePermission.deleted_at.is_(None)
    ).first()
    
    if not role_permission:
        log.warning(f"角色权限关联未找到: id={role_permission_id}")
        return error_response(code=404, msg="角色权限关联未找到")
    
    # 执行软删除
    role_permission.deleted_at = datetime.now()
    db.commit()
    
    log.info(f"成功删除角色权限关联: id={role_permission.id}")
    
    return success_response(data={"deleted_id": role_permission_id})


@router.delete("/", response_model=ResponseModel, summary="批量删除角色权限关联（软删除）", dependencies=[Depends(get_current_user_info), Depends(require_permission('ROLE_PERMISSION_ASSIGN'))])
def delete_role_permissions(delete_request: RolePermissionDeleteRequest, db: Session = Depends(get_db)):
    """
    批量软删除角色权限关联
    
    - **role_permission_ids**: 要删除的角色权限关联ID列表
    """
    log.info(f"批量删除角色权限关联: ids={delete_request.role_permission_ids}")
    
    # 查找未被软删除的关联
    role_permissions = db.query(RolePermission).filter(
        RolePermission.id.in_(delete_request.role_permission_ids),
        RolePermission.deleted_at.is_(None)
    ).all()
    
    if not role_permissions:
        log.warning(f"未找到可删除的角色权限关联: {delete_request.role_permission_ids}")
        return error_response(code=404, msg="未找到可删除的角色权限关联")
    
    # 执行软删除
    deleted_count = 0
    deleted_ids = []
    
    for role_permission in role_permissions:
        role_permission.deleted_at = datetime.now()
        deleted_count += 1
        deleted_ids.append(role_permission.id)
    
    db.commit()
    log.info(f"成功软删除 {deleted_count} 个角色权限关联: {deleted_ids}")
    
    return success_response(data={
        "deleted_count": deleted_count,
        "deleted_ids": deleted_ids
    })
