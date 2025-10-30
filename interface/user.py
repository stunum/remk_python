"""
用户管理API
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from database import db, DatabaseError
from models.user import User

router = APIRouter()


class UserCreate(BaseModel):
    """用户创建模型"""
    username: str
    password: str
    email: str
    full_name: str
    user_type: str
    status: str = "active"


class UserResponse(BaseModel):
    """用户响应模型"""
    id: int
    username: str
    email: str
    full_name: str
    user_type: str
    status: str

    class Config:
        from_attributes = True


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate):
    """创建新用户"""
    try:
        # 检查用户名是否已存在
        existing_users = db.find(User, username=user_data.username)
        if existing_users:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 创建新用户
        new_user = User(
            username=user_data.username,
            password_hash=user_data.password,  # 实际应用中应该对密码进行哈希处理
            email=user_data.email,
            full_name=user_data.full_name,
            user_type=user_data.user_type,
            status=user_data.status
        )
        
        created_user = db.create(new_user)
        return created_user
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )


@router.get("/", response_model=List[UserResponse])
async def get_users():
    """获取所有用户"""
    try:
        users = db.get_all(User)
        return users
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """根据ID获取用户"""
    try:
        user = db.get_by_id(User, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"用户ID {user_id} 不存在"
            )
        return user
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )