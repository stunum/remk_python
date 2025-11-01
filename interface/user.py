from typing import Annotated, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field as PydanticField
from models.user import User
from database import get_db
from typing import List
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log  # 导入全局日志对象

router = APIRouter()


class UserCreate(BaseModel):
    """用户创建模型"""
    username: str = PydanticField(..., min_length=3, max_length=50, description="用户名")
    password_hash: str = PydanticField(..., min_length=6, max_length=255, description="密码哈希")
    email: Optional[EmailStr] = None
    phone: Optional[str] = PydanticField(None, max_length=20)
    full_name: str = PydanticField(..., min_length=1, max_length=100, description="姓名")
    user_type: str = PydanticField(default='doctor', pattern='^(admin|doctor|technician|viewer)$')
    department: Optional[str] = PydanticField(None, max_length=100)
    title: Optional[str] = PydanticField(None, max_length=50)
    license_number: Optional[str] = PydanticField(None, max_length=50)
    status: str = PydanticField(default='active', pattern='^(active|inactive|locked)$')
    created_by: Optional[int] = None


class UserUpdate(BaseModel):
    """用户更新模型"""
    password_hash: Optional[str] = PydanticField(None, min_length=6, max_length=255, description="密码哈希")
    email: Optional[EmailStr] = None
    phone: Optional[str] = PydanticField(None, max_length=20)
    full_name: Optional[str] = PydanticField(None, min_length=1, max_length=100)
    user_type: Optional[str] = PydanticField(None, pattern='^(admin|doctor|technician|viewer)$')
    department: Optional[str] = PydanticField(None, max_length=100)
    title: Optional[str] = PydanticField(None, max_length=50)
    license_number: Optional[str] = PydanticField(None, max_length=50)
    status: Optional[str] = PydanticField(None, pattern='^(active|inactive|locked)$')
    updated_by: Optional[int] = None


class UserResponse(BaseModel):
    """用户响应模型，排除敏感字段"""
    id: int
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: str
    user_type: str
    department: Optional[str] = None
    title: Optional[str] = None
    license_number: Optional[str] = None
    status: str
    
    class Config:
        from_attributes = True


class UserDeleteRequest(BaseModel):
    """批量删除用户请求模型"""
    user_ids: List[int] = PydanticField(..., min_length=1, description="要删除的用户ID列表")
    deleted_by: Optional[int] = PydanticField(None, description="删除操作人ID")


@router.post("/", response_model=ResponseModel)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """创建新用户"""
    # 检查用户名是否已存在
    existing_user = db.query(User).filter(
        User.username == user_data.username,
        User.deleted_at.is_(None)
    ).first()
    if existing_user:
        return error_response(code=400, msg="用户名已存在")
    
    # 检查邮箱是否已存在
    if user_data.email:
        existing_email = db.query(User).filter(
            User.email == user_data.email,
            User.deleted_at.is_(None)
        ).first()
        if existing_email:
            return error_response(code=400, msg="邮箱已被使用")
    
    # 创建用户对象
    new_user = User(**user_data.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    # 返回更新后的用户信息
    user_response = UserResponse.model_validate(new_user)
    return success_response(data=user_response.model_dump())


@router.get("/{user_id}", response_model=ResponseModel)
def find_user(user_id: int, db: Session = Depends(get_db)):
    """根据ID获取单个用户（排除已软删除的用户）"""
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)  # 排除软删除的用户
    ).first()
    if not user:
        return error_response(code=404, msg="用户未找到")
    
    # 转换为响应模型，排除敏感字段
    user_response = UserResponse.model_validate(user)
    return success_response(data=user_response.model_dump())


@router.get("/", response_model=ResponseModel)
def list_users(
        page: int = Query(1, ge=1, description="页码"),
        page_size: int = Query(10, ge=1, le=100, description="每页数量"),
        status: Optional[str] = Query(None, description="用户状态筛选"),
        user_type: Optional[str] = Query(None, description="用户类型筛选"),
        department: Optional[str] = Query(None, description="部门筛选"),
        db: Session = Depends(get_db)):
    """获取用户列表（分页，排除已软删除的用户）"""
    offset = (page - 1) * page_size
    
    # 构建查询，排除软删除的用户
    query = db.query(User).filter(User.deleted_at.is_(None))
    
    # 添加筛选条件
    if status:
        query = query.filter(User.status == status)
    if user_type:
        query = query.filter(User.user_type == user_type)
    if department:
        query = query.filter(User.department == department)
    
    # 获取总数和分页数据
    total = query.count()
    users = query.offset(offset).limit(page_size).all()
    
    # 转换为响应模型列表，排除敏感字段
    users_response = [UserResponse.model_validate(user).model_dump() for user in users]
    
    return success_response(data={
        "users": users_response,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
        }
    })


@router.put("/{user_id}", response_model=ResponseModel)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    """更新用户信息（排除已软删除的用户）"""
    # 查找用户（排除软删除）
    user = db.query(User).filter(
        User.id == user_id,
        User.deleted_at.is_(None)
    ).first()
    if not user:
        return error_response(code=404, msg="用户未找到")
    
    # 检查邮箱是否被其他用户使用
    if user_data.email and user_data.email != user.email:
        existing_email = db.query(User).filter(
            User.email == user_data.email,
            User.id != user_id,
            User.deleted_at.is_(None)
        ).first()
        if existing_email:
            return error_response(code=400, msg="邮箱已被其他用户使用")
    
    # 更新字段（只更新提供的字段）
    update_data = user_data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    # updated_at 会由数据库触发器自动更新
    db.commit()
    db.refresh(user)
    
    # 返回更新后的用户信息
    user_response = UserResponse.model_validate(user)
    return success_response(data=user_response.model_dump())


@router.delete("/", response_model=ResponseModel)
def delete_users(delete_request: UserDeleteRequest, db: Session = Depends(get_db)):
    """批量软删除用户"""
    log.debug(f"批量软删除用户: {delete_request.user_ids}, 删除操作人ID: {delete_request.deleted_by}")
    
    # 查找未被软删除的用户
    users = db.query(User).filter(
        User.id.in_(delete_request.user_ids),
        User.deleted_at.is_(None)  # 只查找未删除的用户
    ).all()
    
    if not users:
        log.warning(f"未找到可删除的用户: {delete_request.user_ids}")
        return error_response(code=404, msg="未找到可删除的用户")
    
    # 执行软删除
    deleted_count = 0
    for user in users:
        user.deleted_at = datetime.now()  # ✅ 使用 Python datetime 对象
        if delete_request.deleted_by:
            user.updated_by = delete_request.deleted_by
        deleted_count += 1
    
    db.commit()
    log.info(f"成功软删除 {deleted_count} 个用户: {[u.id for u in users]}")
    
    return success_response(data={
        "deleted_count": deleted_count,
        "deleted_ids": [user.id for user in users]
    })
