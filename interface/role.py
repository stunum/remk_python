"""
角色管理API - RESTful风格
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField

from models.role import Role
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class RoleCreate(BaseModel):
    """角色创建模型"""
    role_name: str = PydanticField(..., min_length=1, max_length=50, description="角色名称")
    role_code: str = PydanticField(..., min_length=1, max_length=20, description="角色代码")
    description: Optional[str] = PydanticField(None, description="角色描述")
    is_system_role: bool = PydanticField(default=False, description="是否为系统内置角色")
    is_active: bool = PydanticField(default=True, description="是否启用")


class RoleUpdate(BaseModel):
    """角色更新模型"""
    role_name: Optional[str] = PydanticField(None, min_length=1, max_length=50, description="角色名称")
    role_code: str = PydanticField(..., min_length=1, max_length=20, description="角色代码")
    description: Optional[str] = PydanticField(None, description="角色描述")
    is_system_role: bool = PydanticField(default=False, description="是否为系统内置角色")
    is_active: Optional[bool] = PydanticField(None, description="是否启用")


class RoleResponse(BaseModel):
    """角色响应模型"""
    id: int
    role_name: str
    role_code: str
    description: Optional[str] = None
    is_system_role: bool
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class RoleDeleteRequest(BaseModel):
    """批量删除角色请求模型"""
    role_ids: List[int] = PydanticField(..., min_length=1, description="要删除的角色ID列表")


# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建新角色")
def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    """
    创建新角色
    
    - **role_name**: 角色名称（唯一）
    - **role_code**: 角色代码（唯一）
    - **description**: 角色描述
    - **is_system_role**: 是否为系统内置角色
    - **is_active**: 是否启用
    """
    log.info(f"创建新角色: role_name={role_data.role_name}, role_code={role_data.role_code}")
    
    # 检查角色名称是否已存在
    existing_name = db.query(Role).filter(
        Role.role_name == role_data.role_name,
        Role.deleted_at.is_(None)
    ).first()
    if existing_name:
        log.warning(f"角色名称已存在: {role_data.role_name}")
        return error_response(code=400, msg="角色名称已存在")
    
    # 检查角色代码是否已存在
    existing_code = db.query(Role).filter(
        Role.role_code == role_data.role_code,
        Role.deleted_at.is_(None)
    ).first()
    if existing_code:
        log.warning(f"角色代码已存在: {role_data.role_code}")
        return error_response(code=400, msg="角色代码已存在")
    
    # 创建角色对象
    new_role = Role(**role_data.model_dump())
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    log.info(f"成功创建角色: id={new_role.id}, role_name={new_role.role_name}")
    
    role_response = RoleResponse.model_validate(new_role)
    return success_response(data=role_response.model_dump())


@router.get("/{role_id}", response_model=ResponseModel, summary="根据ID获取单个角色")
def get_role(role_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个角色信息（排除已软删除的角色）
    
    - **role_id**: 角色ID
    """
    log.debug(f"查询角色: id={role_id}")
    
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.deleted_at.is_(None)
    ).first()
    
    if not role:
        log.warning(f"角色未找到: id={role_id}")
        return error_response(code=404, msg="角色未找到")
    
    log.debug(f"成功查询角色: id={role.id}, role_name={role.role_name}")
    
    role_response = RoleResponse.model_validate(role)
    return success_response(data=role_response.model_dump())


@router.get("/", response_model=ResponseModel, summary="查询角色列表")
def list_roles(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    is_active: Optional[bool] = Query(None, description="是否启用筛选"),
    is_system_role: Optional[bool] = Query(None, description="是否系统角色筛选"),
    role_name: Optional[str] = Query(None, description="角色名称模糊查询"),
    db: Session = Depends(get_db)
):
    """
    查询角色列表（支持分页和筛选）
    
    支持的筛选条件：
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **is_active**: 是否启用
    - **is_system_role**: 是否系统角色
    - **role_name**: 角色名称模糊查询
    """
    log.debug(f"分页查询角色: page={page}, page_size={page_size}")
    
    offset = (page - 1) * page_size
    
    # 构建查询，排除软删除的角色
    query = db.query(Role).filter(Role.deleted_at.is_(None))
    
    # 添加筛选条件
    if is_active is not None:
        query = query.filter(Role.is_active == is_active)
    if is_system_role is not None:
        query = query.filter(Role.is_system_role == is_system_role)
    if role_name:
        query = query.filter(Role.role_name.like(f"%{role_name}%"))
    
    # 获取总数和分页数据
    total = query.count()
    roles = query.order_by(Role.created_at.desc()).offset(offset).limit(page_size).all()
    
    log.debug(f"查询到 {total} 个角色，当前页 {len(roles)} 个")
    
    # 转换为响应模型列表
    roles_response = [RoleResponse.model_validate(role).model_dump() for role in roles]
    
    return success_response(data={
        "roles": roles_response,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    })


@router.put("/{role_id}", response_model=ResponseModel, summary="更新角色信息")
def update_role(role_id: int, role_data: RoleUpdate, db: Session = Depends(get_db)):
    """
    更新角色信息（排除已软删除的角色）
    
    - **role_id**: 角色ID
    - 只更新提供的字段，未提供的字段保持不变
    - 系统内置角色的 role_code 不可修改
    """
    log.info(f"更新角色信息: id={role_id}")
    
    # 查找角色（排除软删除）
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.deleted_at.is_(None)
    ).first()
    
    if not role:
        log.warning(f"角色未找到: id={role_id}")
        return error_response(code=404, msg="角色未找到")
    
    # 检查角色名称是否被其他角色使用
    if role_data.role_name and role_data.role_name != role.role_name:
        existing_name = db.query(Role).filter(
            Role.role_name == role_data.role_name,
            Role.id != role_id,
            Role.deleted_at.is_(None)
        ).first()
        if existing_name:
            log.warning(f"角色名称已被使用: {role_data.role_name}")
            return error_response(code=400, msg="角色名称已被其他角色使用")
    
    # 更新字段（只更新提供的字段）
    update_data = role_data.model_dump(exclude_unset=True)
    if not update_data:
        log.warning(f"没有提供任何更新字段: id={role_id}")
        return error_response(code=400, msg="没有提供任何更新字段")
    
    for key, value in update_data.items():
        setattr(role, key, value)
    
    db.commit()
    db.refresh(role)
    
    log.info(f"成功更新角色: id={role.id}, role_name={role.role_name}")
    
    role_response = RoleResponse.model_validate(role)
    return success_response(data=role_response.model_dump())


@router.delete("/{role_id}", response_model=ResponseModel, summary="删除单个角色（软删除）")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    """
    删除单个角色（软删除）
    
    - **role_id**: 角色ID
    - 系统内置角色不可删除
    """
    log.info(f"删除角色: id={role_id}")
    
    role = db.query(Role).filter(
        Role.id == role_id,
        Role.deleted_at.is_(None)
    ).first()
    
    if not role:
        log.warning(f"角色未找到: id={role_id}")
        return error_response(code=404, msg="角色未找到")
    
    # 系统内置角色不可删除
    if role.is_system_role:
        log.warning(f"系统内置角色不可删除: id={role_id}")
        return error_response(code=403, msg="系统内置角色不可删除")
    
    # 执行软删除
    role.deleted_at = datetime.now()
    db.commit()
    
    log.info(f"成功删除角色: id={role.id}, role_name={role.role_name}")
    
    return success_response(data={"deleted_id": role_id})


@router.delete("/", response_model=ResponseModel, summary="批量删除角色（软删除）")
def delete_roles(delete_request: RoleDeleteRequest, db: Session = Depends(get_db)):
    """
    批量软删除角色
    
    - **role_ids**: 要删除的角色ID列表
    - 系统内置角色不会被删除
    """
    log.info(f"批量删除角色: ids={delete_request.role_ids}")
    
    # 查找未被软删除的角色
    roles = db.query(Role).filter(
        Role.id.in_(delete_request.role_ids),
        Role.deleted_at.is_(None)
    ).all()
    
    if not roles:
        log.warning(f"未找到可删除的角色: {delete_request.role_ids}")
        return error_response(code=404, msg="未找到可删除的角色")
    
    # 执行软删除（跳过系统内置角色）
    deleted_count = 0
    deleted_ids = []
    skipped_count = 0
    
    for role in roles:
        if role.is_system_role:
            skipped_count += 1
            continue
        
        role.deleted_at = datetime.now()
        deleted_count += 1
        deleted_ids.append(role.id)
    
    db.commit()
    log.info(f"成功软删除 {deleted_count} 个角色，跳过 {skipped_count} 个系统角色: {deleted_ids}")
    
    return success_response(data={
        "deleted_count": deleted_count,
        "deleted_ids": deleted_ids,
        "skipped_count": skipped_count
    })

