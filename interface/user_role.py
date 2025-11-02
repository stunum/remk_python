"""
用户角色关联管理API - RESTful风格
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField

from models.user_role import UserRole
from models.user import User
from models.role import Role
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class UserRoleCreate(BaseModel):
    """用户角色关联创建模型"""
    user_id: int = PydanticField(..., description="用户ID")
    role_id: int = PydanticField(..., description="角色ID")
    assigned_by: Optional[int] = PydanticField(None, description="分配人ID")
    is_active: bool = PydanticField(default=True, description="是否有效")


class UserRoleUpdate(BaseModel):
    """用户角色关联更新模型"""
    is_active: Optional[bool] = PydanticField(None, description="是否有效")


class UserRoleResponse(BaseModel):
    """用户角色关联响应模型"""
    id: int
    user_id: int
    role_id: int
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[int] = None
    is_active: bool
    
    class Config:
        from_attributes = True


class UserRoleDetailResponse(BaseModel):
    """用户角色关联详细响应模型（包含用户和角色信息）"""
    id: int
    user_id: int
    user_name: Optional[str] = None
    role_id: int
    role_name: Optional[str] = None
    role_code: Optional[str] = None
    assigned_at: Optional[datetime] = None
    assigned_by: Optional[int] = None
    is_active: bool


class UserRoleDeleteRequest(BaseModel):
    """批量删除用户角色关联请求模型"""
    user_role_ids: List[int] = PydanticField(..., min_length=1, description="要删除的用户角色关联ID列表")


# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建用户角色关联")
def create_user_role(user_role_data: UserRoleCreate, db: Session = Depends(get_db)):
    """
    创建用户角色关联
    
    - **user_id**: 用户ID
    - **role_id**: 角色ID
    - **assigned_by**: 分配人ID
    - **is_active**: 是否有效
    """
    log.info(f"创建用户角色关联: user_id={user_role_data.user_id}, role_id={user_role_data.role_id}")
    
    # 检查用户是否存在
    user = db.query(User).filter(User.id == user_role_data.user_id, User.deleted_at.is_(None)).first()
    if not user:
        log.warning(f"用户不存在: user_id={user_role_data.user_id}")
        return error_response(code=404, msg="用户不存在")
    
    # 检查角色是否存在
    role = db.query(Role).filter(Role.id == user_role_data.role_id, Role.deleted_at.is_(None)).first()
    if not role:
        log.warning(f"角色不存在: role_id={user_role_data.role_id}")
        return error_response(code=404, msg="角色不存在")
    
    # 检查关联是否已存在
    existing = db.query(UserRole).filter(
        UserRole.user_id == user_role_data.user_id,
        UserRole.role_id == user_role_data.role_id,
        UserRole.deleted_at.is_(None)
    ).first()
    if existing:
        log.warning(f"用户角色关联已存在: user_id={user_role_data.user_id}, role_id={user_role_data.role_id}")
        return error_response(code=400, msg="用户角色关联已存在")
    
    # 创建用户角色关联
    new_user_role = UserRole(**user_role_data.model_dump())
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    
    log.info(f"成功创建用户角色关联: id={new_user_role.id}")
    
    user_role_response = UserRoleResponse.model_validate(new_user_role)
    return success_response(data=user_role_response.model_dump())


@router.get("/{user_role_id}", response_model=ResponseModel, summary="根据ID获取用户角色关联")
def get_user_role(user_role_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取用户角色关联信息（排除已软删除的关联）
    
    - **user_role_id**: 用户角色关联ID
    """
    log.debug(f"查询用户角色关联: id={user_role_id}")
    
    user_role = db.query(UserRole).filter(
        UserRole.id == user_role_id,
        UserRole.deleted_at.is_(None)
    ).first()
    
    if not user_role:
        log.warning(f"用户角色关联未找到: id={user_role_id}")
        return error_response(code=404, msg="用户角色关联未找到")
    
    # 获取关联的用户和角色信息
    user = db.query(User).filter(User.id == user_role.user_id).first()
    role = db.query(Role).filter(Role.id == user_role.role_id).first()
    
    detail_response = UserRoleDetailResponse(
        id=user_role.id,
        user_id=user_role.user_id,
        user_name=user.username if user else None,
        role_id=user_role.role_id,
        role_name=role.role_name if role else None,
        role_code=role.role_code if role else None,
        assigned_at=user_role.assigned_at,
        assigned_by=user_role.assigned_by,
        is_active=user_role.is_active
    )
    
    return success_response(data=detail_response.model_dump())


@router.get("/", response_model=ResponseModel, summary="查询用户角色关联列表")
def list_user_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    user_id: Optional[int] = Query(None, description="用户ID筛选"),
    role_id: Optional[int] = Query(None, description="角色ID筛选"),
    is_active: Optional[bool] = Query(None, description="是否有效筛选"),
    db: Session = Depends(get_db)
):
    """
    查询用户角色关联列表（支持分页和筛选）
    
    支持的筛选条件：
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **user_id**: 用户ID
    - **role_id**: 角色ID
    - **is_active**: 是否有效
    """
    log.debug(f"分页查询用户角色关联: page={page}, page_size={page_size}")
    
    offset = (page - 1) * page_size
    
    # 构建查询用于计算总数，排除软删除的关联
    count_query = db.query(UserRole).filter(UserRole.deleted_at.is_(None))
    
    # 添加筛选条件
    if user_id is not None:
        count_query = count_query.filter(UserRole.user_id == user_id)
    if role_id is not None:
        count_query = count_query.filter(UserRole.role_id == role_id)
    if is_active is not None:
        count_query = count_query.filter(UserRole.is_active == is_active)
    
    # 获取总数
    total = count_query.count()
    
    # 重新构建查询用于获取分页数据
    data_query = db.query(UserRole).filter(UserRole.deleted_at.is_(None))
    
    # 添加筛选条件
    if user_id is not None:
        data_query = data_query.filter(UserRole.user_id == user_id)
    if role_id is not None:
        data_query = data_query.filter(UserRole.role_id == role_id)
    if is_active is not None:
        data_query = data_query.filter(UserRole.is_active == is_active)
    
    # 获取分页数据
    user_roles = data_query.order_by(UserRole.assigned_at.desc()).offset(offset).limit(page_size).all()
    
    log.debug(f"查询到 {total} 个用户角色关联，当前页 {len(user_roles)} 个")
    
    # 转换为详细响应模型列表
    user_roles_response = []
    for user_role in user_roles:
        user = db.query(User).filter(User.id == user_role.user_id).first()
        role = db.query(Role).filter(Role.id == user_role.role_id).first()
        
        detail_response = UserRoleDetailResponse(
            id=user_role.id,
            user_id=user_role.user_id,
            user_name=user.username if user else None,
            role_id=user_role.role_id,
            role_name=role.role_name if role else None,
            role_code=role.role_code if role else None,
            assigned_at=user_role.assigned_at,
            assigned_by=user_role.assigned_by,
            is_active=user_role.is_active
        )
        user_roles_response.append(detail_response.model_dump())
    
    return success_response(data={
        "user_roles": user_roles_response,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    })


@router.put("/{user_role_id}", response_model=ResponseModel, summary="更新用户角色关联")
def update_user_role(user_role_id: int, user_role_data: UserRoleUpdate, db: Session = Depends(get_db)):
    """
    更新用户角色关联（排除已软删除的关联）
    
    - **user_role_id**: 用户角色关联ID
    - 只更新提供的字段，未提供的字段保持不变
    """
    log.info(f"更新用户角色关联: id={user_role_id}")
    
    # 查找用户角色关联（排除软删除）
    user_role = db.query(UserRole).filter(
        UserRole.id == user_role_id,
        UserRole.deleted_at.is_(None)
    ).first()
    
    if not user_role:
        log.warning(f"用户角色关联未找到: id={user_role_id}")
        return error_response(code=404, msg="用户角色关联未找到")
    
    # 更新字段（只更新提供的字段）
    update_data = user_role_data.model_dump(exclude_unset=True)
    if not update_data:
        log.warning(f"没有提供任何更新字段: id={user_role_id}")
        return error_response(code=400, msg="没有提供任何更新字段")
    
    for key, value in update_data.items():
        setattr(user_role, key, value)
    
    db.commit()
    db.refresh(user_role)
    
    log.info(f"成功更新用户角色关联: id={user_role.id}")
    
    user_role_response = UserRoleResponse.model_validate(user_role)
    return success_response(data=user_role_response.model_dump())


@router.delete("/{user_role_id}", response_model=ResponseModel, summary="删除用户角色关联（软删除）")
def delete_user_role(user_role_id: int, db: Session = Depends(get_db)):
    """
    删除用户角色关联（软删除）
    
    - **user_role_id**: 用户角色关联ID
    """
    log.info(f"删除用户角色关联: id={user_role_id}")
    
    user_role = db.query(UserRole).filter(
        UserRole.id == user_role_id,
        UserRole.deleted_at.is_(None)
    ).first()
    
    if not user_role:
        log.warning(f"用户角色关联未找到: id={user_role_id}")
        return error_response(code=404, msg="用户角色关联未找到")
    
    # 执行软删除
    user_role.deleted_at = datetime.now()
    db.commit()
    
    log.info(f"成功删除用户角色关联: id={user_role.id}")
    
    return success_response(data={"deleted_id": user_role_id})


@router.delete("/", response_model=ResponseModel, summary="批量删除用户角色关联（软删除）")
def delete_user_roles(delete_request: UserRoleDeleteRequest, db: Session = Depends(get_db)):
    """
    批量软删除用户角色关联
    
    - **user_role_ids**: 要删除的用户角色关联ID列表
    """
    log.info(f"批量删除用户角色关联: ids={delete_request.user_role_ids}")
    
    # 查找未被软删除的关联
    user_roles = db.query(UserRole).filter(
        UserRole.id.in_(delete_request.user_role_ids),
        UserRole.deleted_at.is_(None)
    ).all()
    
    if not user_roles:
        log.warning(f"未找到可删除的用户角色关联: {delete_request.user_role_ids}")
        return error_response(code=404, msg="未找到可删除的用户角色关联")
    
    # 执行软删除
    deleted_count = 0
    deleted_ids = []
    
    for user_role in user_roles:
        user_role.deleted_at = datetime.now()
        deleted_count += 1
        deleted_ids.append(user_role.id)
    
    db.commit()
    log.info(f"成功软删除 {deleted_count} 个用户角色关联: {deleted_ids}")
    
    return success_response(data={
        "deleted_count": deleted_count,
        "deleted_ids": deleted_ids
    })

