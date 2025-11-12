"""
认证管理API
提供用户登录、令牌刷新、用户验证等功能
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField

from models.user import User
from models.user_role import UserRole
from models.role_permission import RolePermission
from models.permission import Permission
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from utils.jwt_auth import (
    verify_password,
    hash_password,
    create_token_pair,
    refresh_access_token,
    get_current_user_id,
    get_current_user_info,
    decode_token
)
from loguru_logging import log

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class LoginRequest(BaseModel):
    """登录请求模型"""
    username: str = PydanticField(..., min_length=3, max_length=50, description="用户名")
    password: str = PydanticField(..., min_length=6, description="密码（前端已加密）")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "hashed_password_from_frontend"
            }
        }


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求模型"""
    refresh_token: str = PydanticField(..., description="刷新令牌")

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
            }
        }


class ChangePasswordRequest(BaseModel):
    """修改密码请求模型"""
    old_password: str = PydanticField(..., min_length=6, description="旧密码（前端已加密）")
    new_password: str = PydanticField(..., min_length=6, description="新密码（前端已加密）")

    class Config:
        json_schema_extra = {
            "example": {
                "old_password": "old_hashed_password",
                "new_password": "new_hashed_password"
            }
        }


class LoginResponse(BaseModel):
    """登录响应模型"""
    token: str = PydanticField(..., description="访问令牌")
    refresh_token: str = PydanticField(..., description="刷新令牌")
    token_type: str = PydanticField(default="bearer", description="令牌类型")
    expires_at: int = PydanticField(..., description="过期时间戳（秒）")
    expires_in: int = PydanticField(..., description="有效期（秒）")
    user: dict = PydanticField(..., description="用户信息")
    permissions: list = PydanticField(default=[], description="用户权限列表")


class UserInfoResponse(BaseModel):
    """用户信息响应模型"""
    id: int
    username: str
    email: Optional[str]
    phone: Optional[str]
    full_name: str
    user_type: str
    department: Optional[str]
    title: Optional[str]
    status: str

    class Config:
        from_attributes = True


# ==================== API 端点 ====================

def get_user_permissions(session: Session, user_id: int, user_type: str) -> list:
    """
    聚合用户有效权限(permission_code列表)
    - admin用户返回全部有效权限
    - 其他用户通过用户角色→角色权限→权限聚合
    """
    if user_type == 'admin':
        perms = session.query(Permission.permission_code).filter(
            Permission.is_active.is_(True),
            Permission.deleted_at.is_(None)
        ).all()
        return [p[0] for p in perms]

    role_ids = session.query(UserRole.role_id).filter(
        UserRole.user_id == user_id,
        UserRole.is_active.is_(True),
        UserRole.deleted_at.is_(None)
    ).all()
    if not role_ids:
        return []
    role_id_list = [r[0] for r in role_ids]

    perm_ids = session.query(RolePermission.permission_id).filter(
        RolePermission.role_id.in_(role_id_list),
        RolePermission.is_active.is_(True),
        RolePermission.deleted_at.is_(None)
    ).all()
    if not perm_ids:
        return []
    perm_id_list = [rp[0] for rp in perm_ids]

    perms = session.query(Permission.permission_code).filter(
        Permission.id.in_(perm_id_list),
        Permission.is_active.is_(True),
        Permission.deleted_at.is_(None)
    ).all()
    return [p[0] for p in perms]

@router.post("/login", response_model=ResponseModel, summary="用户登录")
async def login(
    login_data: LoginRequest,
    session: Session = Depends(get_db)
):
    """
    用户登录接口
    
    - **username**: 用户名
    - **password**: 密码（前端已使用SHA-256加密）
    
    返回JWT访问令牌和刷新令牌
    """
    try:
        # 查询用户
        user = session.query(User).filter(
            User.username == login_data.username,
            User.deleted_at.is_(None)
        ).first()
        
        if not user:
            log.warning(f"登录失败: 用户不存在 - {login_data.username}")
            return error_response(msg="用户名或密码错误", code=401)
        
        # 检查用户状态
        if user.status != 'active':
            log.warning(f"登录失败: 用户状态异常 - {login_data.username}, 状态={user.status}")
            return error_response(msg=f"用户账号已{user.status}", code=403)
        
        # 验证密码
        # 注意：前端传来的password已经是SHA-256哈希值
        # 我们需要将它与数据库中的bcrypt哈希进行比对
        if not verify_password(login_data.password, user.password_hash):
            log.warning(f"登录失败: 密码错误 - {login_data.username}")
            return error_response(msg="用户名或密码错误", code=401)
        
        # 聚合用户权限
        permissions = get_user_permissions(session, user.id, user.user_type)
        
        # 创建令牌对
        token_data = create_token_pair(
            user_id=user.id,
            username=user.username,
            user_type=user.user_type,
            permissions=permissions
        )
        
        # 更新最后登录时间
        user.last_login_at = datetime.now()
        session.commit()
        
        # 构建响应
        response_data = {
            "token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "token_type": token_data["token_type"],
            "expires_at": token_data["expires_at"],
            "expires_in": token_data["expires_in"],
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "full_name": user.full_name,
                "user_type": user.user_type,
                "department": user.department,
                "title": user.title,
                "status": user.status
            },
            "permissions": permissions
        }
        
        log.info(f"用户登录成功: {user.username} (ID={user.id})")
        return success_response(data=response_data, msg="登录成功")
    
    except Exception as e:
        log.error(f"登录失败: {str(e)}")
        return error_response(msg=f"登录失败: {str(e)}", code=500)


@router.post("/refresh", response_model=ResponseModel, summary="刷新访问令牌")
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    session: Session = Depends(get_db)
):
    """
    使用刷新令牌获取新的访问令牌
    
    - **refresh_token**: 刷新令牌
    
    返回新的JWT访问令牌和刷新令牌
    """
    try:
        # 验证刷新令牌并提取用户信息
        payload = decode_token(refresh_data.refresh_token)
        user_id = payload.get("user_id")
        
        # 验证用户仍然存在且状态正常
        user = session.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None)
        ).first()
        
        if not user:
            log.warning(f"刷新令牌失败: 用户不存在 - ID={user_id}")
            return error_response(msg="用户不存在", code=401)
        
        if user.status != 'active':
            log.warning(f"刷新令牌失败: 用户状态异常 - {user.username}, 状态={user.status}")
            return error_response(msg=f"用户账号已{user.status}", code=403)
        
        # 重新聚合权限并生成新令牌对
        permissions = get_user_permissions(session, user.id, user.user_type)
        token_data = create_token_pair(
            user_id=user.id,
            username=user.username,
            user_type=user.user_type,
            permissions=permissions
        )

        # 构建响应
        response_data = {
            "token": token_data["access_token"],
            "refresh_token": token_data["refresh_token"],
            "token_type": token_data["token_type"],
            "expires_at": token_data["expires_at"],
            "expires_in": token_data["expires_in"]
        }
        
        log.info(f"令牌刷新成功: {user.username} (ID={user.id})")
        return success_response(data=response_data, msg="令牌刷新成功")
    
    except HTTPException as e:
        return error_response(msg=e.detail, code=e.status_code)
    except Exception as e:
        log.error(f"刷新令牌失败: {str(e)}")
        return error_response(msg=f"刷新令牌失败: {str(e)}", code=500)


@router.post("/validate", response_model=ResponseModel, summary="验证令牌")
async def validate_token(
    user_info: dict = Depends(get_current_user_info)
):
    """
    验证访问令牌是否有效
    
    需要在请求头中携带: Authorization: Bearer <token>
    
    返回令牌中的用户信息
    """
    try:
        return success_response(data=user_info, msg="令牌有效")
    except HTTPException as e:
        return error_response(msg=e.detail, code=e.status_code)
    except Exception as e:
        log.error(f"验证令牌失败: {str(e)}")
        return error_response(msg=f"验证令牌失败: {str(e)}", code=500)


@router.post("/logout", response_model=ResponseModel, summary="用户退出登录")
async def logout(
    user_id: int = Depends(get_current_user_id)
):
    """
    用户退出登录
    
    需要在请求头中携带: Authorization: Bearer <token>
    
    注意：JWT是无状态的，服务端不存储令牌
    实际的登出操作由前端清除令牌完成
    此接口主要用于日志记录和可能的额外处理
    """
    try:
        log.info(f"用户退出登录: ID={user_id}")
        return success_response(msg="退出登录成功")
    except Exception as e:
        log.error(f"退出登录失败: {str(e)}")
        return error_response(msg=f"退出登录失败: {str(e)}", code=500)


@router.get("/user", response_model=ResponseModel, summary="获取当前用户信息")
async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_db)
):
    """
    获取当前登录用户的详细信息
    
    需要在请求头中携带: Authorization: Bearer <token>
    """
    try:
        user = session.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None)
        ).first()
        
        if not user:
            log.warning(f"获取用户信息失败: 用户不存在 - ID={user_id}")
            return error_response(msg="用户不存在", code=404)
        
        user_info = UserInfoResponse.model_validate(user).model_dump()
        
        log.info(f"获取用户信息成功: {user.username} (ID={user.id})")
        return success_response(data=user_info)
    
    except Exception as e:
        log.error(f"获取用户信息失败: {str(e)}")
        return error_response(msg=f"获取用户信息失败: {str(e)}", code=500)


@router.post("/change-password", response_model=ResponseModel, summary="修改密码")
async def change_password(
    password_data: ChangePasswordRequest,
    user_id: int = Depends(get_current_user_id),
    session: Session = Depends(get_db)
):
    """
    修改当前用户密码
    
    需要在请求头中携带: Authorization: Bearer <token>
    
    - **old_password**: 旧密码（前端已加密）
    - **new_password**: 新密码（前端已加密）
    """
    try:
        # 查询用户
        user = session.query(User).filter(
            User.id == user_id,
            User.deleted_at.is_(None)
        ).first()
        
        if not user:
            log.warning(f"修改密码失败: 用户不存在 - ID={user_id}")
            return error_response(msg="用户不存在", code=404)
        
        # 验证旧密码
        if not verify_password(password_data.old_password, user.password_hash):
            log.warning(f"修改密码失败: 旧密码错误 - {user.username}")
            return error_response(msg="旧密码错误", code=400)
        
        # 更新密码
        user.password_hash = hash_password(password_data.new_password)
        user.updated_at = datetime.now()
        session.commit()
        
        log.info(f"密码修改成功: {user.username} (ID={user.id})")
        return success_response(msg="密码修改成功")
    
    except Exception as e:
        session.rollback()
        log.error(f"修改密码失败: {str(e)}")
        return error_response(msg=f"修改密码失败: {str(e)}", code=500)
