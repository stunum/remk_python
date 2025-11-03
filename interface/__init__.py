"""
API接口模块
"""
from fastapi import APIRouter

# 创建主路由器
api_router = APIRouter()

# 导入并包含所有子路由器
from .auth import router as auth_router
from .user import router as user_router
from .patient import router as patient_router
from .examination import router as examination_router
from .registration import router as registration_router
from .fundus_image import router as fundus_image_router
from .fundus_image_save import router as fundus_image_save_router
from .role import router as role_router
from .permission import router as permission_router
from .user_role import router as user_role_router
from .role_permission import router as role_permission_router
from .system_log import router as system_log_router
from .config_management import router as config_management_router

# 注册所有子路由器
api_router.include_router(auth_router, prefix="/auth", tags=["认证管理"])
api_router.include_router(user_router, prefix="/users", tags=["用户管理"])
api_router.include_router(patient_router, prefix="/patients", tags=["患者管理"])
api_router.include_router(examination_router, prefix="/examinations", tags=["检查管理"])
api_router.include_router(registration_router, prefix="/registrations", tags=["挂号管理"])
api_router.include_router(fundus_image_router, prefix="/fundus-images", tags=["眼底图像管理"])
api_router.include_router(fundus_image_save_router, prefix="/images", tags=["图像保存"])
api_router.include_router(role_router, prefix="/roles", tags=["角色管理"])
api_router.include_router(permission_router, prefix="/permissions", tags=["权限管理"])
api_router.include_router(user_role_router, prefix="/user-roles", tags=["用户角色关联"])
api_router.include_router(role_permission_router, prefix="/role-permissions", tags=["角色权限关联"])
api_router.include_router(system_log_router, prefix="/system-logs", tags=["系统日志"])
api_router.include_router(config_management_router, prefix="/config", tags=["配置管理"])