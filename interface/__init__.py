"""
API接口模块
"""
from fastapi import APIRouter

# 创建主路由器
api_router = APIRouter()

# 导入并包含所有子路由器
from .user import router as user_router
from .patient import router as patient_router
from .examination import router as examination_router
from .registration import router as registration_router
from .fundus_image import router as fundus_image_router

# 注册所有子路由器
api_router.include_router(user_router, prefix="/users", tags=["用户管理"])
api_router.include_router(patient_router, prefix="/patients", tags=["患者管理"])
api_router.include_router(examination_router, prefix="/examinations", tags=["检查管理"])
api_router.include_router(registration_router, prefix="/registrations", tags=["挂号管理"])
api_router.include_router(fundus_image_router, prefix="/fundus-images", tags=["眼底图像管理"])