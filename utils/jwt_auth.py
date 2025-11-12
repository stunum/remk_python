"""
JWT认证工具模块
提供JWT令牌的生成、验证和管理功能
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import hashlib
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from loguru_logging import log
from config import config as app_config

# 从配置文件加载JWT相关参数
_jwt_config = app_config.config.jwt
PASSWORD_SALT = _jwt_config.password_salt
SECRET_KEY = _jwt_config.secret_key
ALGORITHM = _jwt_config.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = _jwt_config.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_DAYS = _jwt_config.refresh_token_expire_days

# HTTP Bearer安全方案
security = HTTPBearer()


def hash_password(password: str) -> str:
    """
    对密码进行哈希加密
    
    Args:
        password: 原始密码（通常是前端SHA-256哈希后的值）
        
    Returns:
        str: 加密后的密码哈希（使用SHA-256 + 盐值）
        
    Note:
        前端传来的密码已经是SHA-256哈希值（64位十六进制）
        后端再次使用SHA-256 + 盐值进行加密，形成双重保护
    """
    # 使用SHA-256 + 盐值进行哈希
    salted = f"{password}{PASSWORD_SALT}"
    hashed = hashlib.sha256(salted.encode('utf-8')).hexdigest()
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配
    
    Args:
        plain_password: 原始密码（前端SHA-256哈希后的值）
        hashed_password: 数据库中存储的密码哈希
        
    Returns:
        bool: 密码是否匹配
    """
    try:
        # 对输入密码进行相同的哈希处理
        input_hash = hash_password(plain_password)
        # 比较哈希值
        return input_hash == hashed_password
    except Exception as e:
        log.error(f"密码验证失败: {str(e)}")
        return False


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    创建访问令牌
    
    Args:
        data: 要编码到令牌中的数据
        expires_delta: 令牌过期时间间隔
        
    Returns:
        str: JWT访问令牌
    """
    to_encode = data.copy()
    
    # 设置过期时间
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # 添加标准JWT声明
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "eyes_remk_system",  # 签发者
        "type": "access"
    })
    
    # 生成JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    创建刷新令牌
    
    Args:
        data: 要编码到令牌中的数据
        
    Returns:
        str: JWT刷新令牌
    """
    to_encode = data.copy()
    
    # 设置过期时间（刷新令牌有效期更长）
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    
    # 添加标准JWT声明
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "iss": "eyes_remk_system",
        "type": "refresh"
    })
    
    # 生成JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    解码并验证JWT令牌
    
    Args:
        token: JWT令牌
        
    Returns:
        Dict[str, Any]: 解码后的令牌数据
        
    Raises:
        HTTPException: 令牌无效或过期
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        log.warning(f"JWT解码失败: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_token(token: str, token_type: str = "access") -> Dict[str, Any]:
    """
    验证令牌并检查类型
    
    Args:
        token: JWT令牌
        token_type: 令牌类型（access或refresh）
        
    Returns:
        Dict[str, Any]: 解码后的令牌数据
        
    Raises:
        HTTPException: 令牌无效、过期或类型不匹配
    """
    payload = decode_token(token)
    
    # 检查令牌类型
    if payload.get("type") != token_type:
        log.warning(f"令牌类型不匹配: 期望={token_type}, 实际={payload.get('type')}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌类型不匹配",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    """
    从JWT令牌中获取当前用户ID（用于依赖注入）
    
    Args:
        credentials: HTTP Bearer凭证
        
    Returns:
        int: 用户ID
        
    Raises:
        HTTPException: 令牌无效或用户ID不存在
    """
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    user_id = payload.get("user_id")
    if user_id is None:
        log.warning("JWT令牌中缺少user_id")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def get_current_user_info(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    从JWT令牌中获取当前用户完整信息（用于依赖注入）
    
    Args:
        credentials: HTTP Bearer凭证
        
    Returns:
        Dict[str, Any]: 用户信息
        
    Raises:
        HTTPException: 令牌无效
    """
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    return {
        "user_id": payload.get("user_id"),
        "username": payload.get("username"),
        "user_type": payload.get("user_type"),
        "permissions": payload.get("permissions", [])
    }


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    从JWT令牌中获取当前用户信息（用于依赖注入）
    这是get_current_user_info的别名，用于简化接口定义
    
    Args:
        credentials: HTTP Bearer凭证
        
    Returns:
        Dict[str, Any]: 用户信息
        
    Raises:
        HTTPException: 令牌无效
    """
    return get_current_user_info(credentials)


def create_token_pair(user_id: int, username: str, user_type: str, permissions: list = None) -> Dict[str, Any]:
    """
    创建访问令牌和刷新令牌对
    
    Args:
        user_id: 用户ID
        username: 用户名
        user_type: 用户类型
        permissions: 用户权限列表
        
    Returns:
        Dict[str, Any]: 包含访问令牌和刷新令牌的字典
    """
    if permissions is None:
        permissions = []
    
    # 准备令牌数据
    token_data = {
        "user_id": user_id,
        "username": username,
        "user_type": user_type,
        "permissions": permissions,
        "sub": str(user_id)  # JWT标准的subject字段
    }
    
    # 创建访问令牌
    access_token = create_access_token(token_data)
    
    # 创建刷新令牌（只包含必要信息）
    refresh_token_data = {
        "user_id": user_id,
        "username": username,
        "sub": str(user_id)
    }
    refresh_token = create_refresh_token(refresh_token_data)
    
    # 计算过期时间
    expires_at = int((datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).timestamp())
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_at": expires_at,
        "expires_in": ACCESS_TOKEN_EXPIRE_MINUTES * 60  # 秒数
    }


def refresh_access_token(refresh_token: str) -> Dict[str, Any]:
    """
    使用刷新令牌获取新的访问令牌
    
    Args:
        refresh_token: 刷新令牌
        
    Returns:
        Dict[str, Any]: 新的令牌对
        
    Raises:
        HTTPException: 刷新令牌无效或过期
    """
    # 验证刷新令牌
    payload = verify_token(refresh_token, token_type="refresh")
    
    user_id = payload.get("user_id")
    username = payload.get("username")
    
    if not user_id or not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的刷新令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 这里应该从数据库查询用户信息以确保用户仍然有效
    # 为了简化，这里假设用户信息不变
    # 实际生产环境应该重新查询用户权限等信息
    
    # 创建新的令牌对
    return create_token_pair(
        user_id=user_id,
        username=username,
        user_type=payload.get("user_type", "doctor"),  # 应该从数据库重新获取
        permissions=payload.get("permissions", [])
    )


# 权限验证装饰器
def require_permission(permission: str):
    """
    检查用户是否有指定权限
    
    Args:
        permission: 所需权限
        
    Returns:
        依赖函数
    """
    def permission_checker(user_info: Dict[str, Any] = Depends(get_current_user_info)) -> Dict[str, Any]:
        permissions = user_info.get("permissions", [])
        if permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要权限: {permission}"
            )
        return user_info
    return permission_checker


def require_user_type(*allowed_types: str):
    """
    检查用户类型是否符合要求
    
    Args:
        allowed_types: 允许的用户类型列表
        
    Returns:
        依赖函数
    """
    def type_checker(user_info: Dict[str, Any] = Depends(get_current_user_info)) -> Dict[str, Any]:
        user_type = user_info.get("user_type")
        if user_type not in allowed_types:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要用户类型: {', '.join(allowed_types)}"
            )
        return user_info
    return type_checker


def require_permissions_any(permissions: list):
    """
    检查用户是否拥有任意一个指定权限
    """
    def checker(user_info: Dict[str, Any] = Depends(get_current_user_info)) -> Dict[str, Any]:
        user_perms = set(user_info.get("permissions", []))
        if not any(p in user_perms for p in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"需要任意权限: {', '.join(permissions)}"
            )
        return user_info
    return checker


def require_permissions_all(permissions: list):
    """
    检查用户是否拥有所有指定权限
    """
    def checker(user_info: Dict[str, Any] = Depends(get_current_user_info)) -> Dict[str, Any]:
        user_perms = set(user_info.get("permissions", []))
        missing = [p for p in permissions if p not in user_perms]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限: {', '.join(missing)}"
            )
        return user_info
    return checker
