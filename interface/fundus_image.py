"""
眼底图像管理API
提供眼底图像的完整CRUD功能，包括：
- 创建眼底图像记录
- 查询眼底图像（单个查询、分页查询）
- 更新眼底图像信息
- 删除眼底图像（单个删除、批量删除，软删除）
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField
from decimal import Decimal

from models.fundus_image import FundusImage
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class FundusImageCreate(BaseModel):
    """眼底图像创建模型"""
    examination_id: int = PydanticField(..., gt=0, description="检查记录ID")
    image_number: str = PydanticField(..., min_length=1,
                                      max_length=50, description="影像编号")
    eye_side: str = PydanticField(..., description="眼别：OS(左眼)/OD(右眼)")
    capture_mode: str = PydanticField(...,
                                      description="拍摄模式：gray(灰度)/color(彩色)")
    image_type: Optional[str] = PydanticField(
        None, max_length=50, description="影像类型")
    image_position: Optional[str] = PydanticField(
        None, max_length=50, description="影像位置")
    file_path: str = PydanticField(..., min_length=1,
                                   max_length=500, description="文件路径")
    file_name: str = PydanticField(..., min_length=1,
                                   max_length=255, description="文件名")
    file_size: Optional[int] = PydanticField(
        None, ge=0, description="文件大小（字节）")
    file_format: Optional[str] = PydanticField(
        None, max_length=20, description="文件格式")
    image_quality: Optional[str] = PydanticField(
        None, description="影像质量：excellent/good/fair/poor")
    resolution: Optional[str] = PydanticField(
        None, max_length=50, description="分辨率")
    acquisition_device: Optional[str] = PydanticField(
        None, max_length=100, description="采集设备")
    acquisition_parameters: Optional[dict] = PydanticField(
        None, description="采集参数（JSON）")
    thumbnail_data: Optional[str] = PydanticField(None, description="缩略图数据")
    is_primary: bool = PydanticField(default=False, description="是否主图")
    upload_status: str = PydanticField(
        default="uploaded", description="上传状态：uploading/uploaded/failed/processing")
    created_by: Optional[int] = PydanticField(None, gt=0, description="创建人ID")

    class Config:
        json_schema_extra = {
            "example": {
                "examination_id": 1,
                "image_number": "IMG20250101001",
                "eye_side": "OD",
                "capture_mode": "color",
                "file_path": "/images/2025/01/01/",
                "file_name": "fundus_001.jpg",
                "file_size": 1024000,
                "file_format": "jpg",
                "image_quality": "excellent",
                "is_primary": True,
                "upload_status": "uploaded"
            }
        }


class FundusImageUpdate(BaseModel):
    """眼底图像更新模型"""
    examination_id: Optional[int] = PydanticField(
        None, gt=0, description="检查记录ID")
    image_number: Optional[str] = PydanticField(
        None, min_length=1, max_length=50, description="影像编号")
    eye_side: Optional[str] = PydanticField(
        None, description="眼别：OS(左眼)/OD(右眼)")
    capture_mode: Optional[str] = PydanticField(
        None, description="拍摄模式：gray(灰度)/color(彩色)")
    image_type: Optional[str] = PydanticField(
        None, max_length=50, description="影像类型")
    image_position: Optional[str] = PydanticField(
        None, max_length=50, description="影像位置")
    file_path: Optional[str] = PydanticField(
        None, max_length=500, description="文件路径")
    file_name: Optional[str] = PydanticField(
        None, max_length=255, description="文件名")
    file_size: Optional[int] = PydanticField(
        None, ge=0, description="文件大小（字节）")
    file_format: Optional[str] = PydanticField(
        None, max_length=20, description="文件格式")
    image_quality: Optional[str] = PydanticField(
        None, description="影像质量：excellent/good/fair/poor")
    resolution: Optional[str] = PydanticField(
        None, max_length=50, description="分辨率")
    acquisition_device: Optional[str] = PydanticField(
        None, max_length=100, description="采集设备")
    acquisition_parameters: Optional[dict] = PydanticField(
        None, description="采集参数（JSON）")
    thumbnail_data: Optional[str] = PydanticField(None, description="缩略图数据")
    is_primary: Optional[bool] = PydanticField(None, description="是否主图")
    upload_status: Optional[str] = PydanticField(
        None, description="上传状态：uploading/uploaded/failed/processing")

    class Config:
        json_schema_extra = {
            "example": {
                "image_quality": "good",
                "upload_status": "uploaded"
            }
        }


class FundusImageResponse(BaseModel):
    """眼底图像响应模型"""
    id: int
    examination_id: int
    image_number: str
    eye_side: str
    capture_mode: str
    image_type: Optional[str]
    image_position: Optional[str]
    file_path: str
    file_name: str
    file_size: Optional[int]
    file_format: Optional[str]
    image_quality: Optional[str]
    resolution: Optional[str]
    acquisition_device: Optional[str]
    acquisition_parameters: Optional[dict]
    thumbnail_data: Optional[str]
    is_primary: bool
    upload_status: str
    deleted_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]

    class Config:
        from_attributes = True


class FundusImageDeleteRequest(BaseModel):
    """眼底图像批量删除请求模型"""
    ids: List[int] = PydanticField(..., min_length=1, description="要删除的图像ID列表")

    class Config:
        json_schema_extra = {
            "example": {
                "ids": [1, 2, 3]
            }
        }


# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建眼底图像记录")
async def create_fundus_image(
    image: FundusImageCreate,
    session: Session = Depends(get_db)
):
    """
    创建新的眼底图像记录

    - **examination_id**: 检查记录ID
    - **image_number**: 影像编号
    - **eye_side**: 眼别（OS/OD）
    - **capture_mode**: 拍摄模式（gray/color）
    - **file_path**: 文件路径
    - **file_name**: 文件名
    """
    try:
        # 创建新图像记录
        db_image = FundusImage(**image.model_dump())
        session.add(db_image)
        session.commit()
        session.refresh(db_image)

        log.info(f"成功创建眼底图像记录: ID={db_image.id}, 影像编号={db_image.image_number}")
        return success_response(
            data=FundusImageResponse.model_validate(db_image).model_dump(),
            msg="眼底图像记录创建成功"
        )

    except Exception as e:
        session.rollback()
        log.error(f"创建眼底图像记录失败: {str(e)}")
        return error_response(msg=f"创建眼底图像记录失败: {str(e)}", code=500)


@router.get("/", response_model=ResponseModel, summary="分页查询眼底图像")
async def get_fundus_images(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    examination_id: Optional[int] = Query(None, description="按检查记录ID筛选"),
    eye_side: Optional[str] = Query(None, description="按眼别筛选"),
    capture_mode: Optional[str] = Query(None, description="按拍摄模式筛选"),
    image_quality: Optional[str] = Query(None, description="按影像质量筛选"),
    upload_status: Optional[str] = Query(None, description="按上传状态筛选"),
    is_primary: Optional[bool] = Query(None, description="按是否主图筛选"),
    include_deleted: bool = Query(False, description="是否包含已删除记录"),
    session: Session = Depends(get_db)
):
    """
    分页查询眼底图像列表

    支持多种筛选条件：
    - 检查记录ID
    - 眼别
    - 拍摄模式
    - 影像质量
    - 上传状态
    - 是否主图
    """
    try:
        # 构建查询
        query = session.query(FundusImage)

        # 应用筛选条件
        if not include_deleted:
            query = query.filter(FundusImage.deleted_at.is_(None))

        if examination_id:
            query = query.filter(FundusImage.examination_id == examination_id)

        if eye_side:
            query = query.filter(FundusImage.eye_side == eye_side)

        if capture_mode:
            query = query.filter(FundusImage.capture_mode == capture_mode)

        if image_quality:
            query = query.filter(FundusImage.image_quality == image_quality)

        if upload_status:
            query = query.filter(FundusImage.upload_status == upload_status)

        if is_primary is not None:
            query = query.filter(FundusImage.is_primary == is_primary)

        # 计算总数
        total = query.count()

        # 分页
        offset = (page - 1) * page_size
        images = query.order_by(FundusImage.created_at.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()

        # 转换为响应模型
        image_list = [FundusImageResponse.model_validate(
            img).model_dump() for img in images]

        log.info(f"查询眼底图像列表成功: 页码={page}, 每页={page_size}, 总数={total}")
        return success_response(data={
            "items": image_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        })

    except Exception as e:
        log.error(f"查询眼底图像列表失败: {str(e)}")
        return error_response(msg=f"查询眼底图像列表失败: {str(e)}", code=500)


@router.get("/{image_id}", response_model=ResponseModel, summary="查询单个眼底图像")
async def get_fundus_image(
    image_id: int,
    session: Session = Depends(get_db)
):
    """
    根据ID查询单个眼底图像记录

    - **image_id**: 图像ID
    """
    try:
        image = session.query(FundusImage).filter(
            FundusImage.id == image_id,
            FundusImage.deleted_at.is_(None)
        ).first()

        if not image:
            log.warning(f"眼底图像不存在: ID={image_id}")
            return error_response(msg="眼底图像不存在", code=404)

        log.info(f"查询眼底图像成功: ID={image_id}")
        return success_response(
            data=FundusImageResponse.model_validate(image).model_dump()
        )

    except Exception as e:
        log.error(f"查询眼底图像失败: {str(e)}")
        return error_response(msg=f"查询眼底图像失败: {str(e)}", code=500)


@router.get("/by-number/{image_number}", response_model=ResponseModel, summary="根据影像编号查询")
async def get_fundus_image_by_number(
    image_number: str,
    session: Session = Depends(get_db)
):
    """
    根据影像编号查询眼底图像

    - **image_number**: 影像编号
    """
    try:
        image = session.query(FundusImage).filter(
            FundusImage.image_number == image_number,
            FundusImage.deleted_at.is_(None)
        ).first()

        if not image:
            log.warning(f"眼底图像不存在: 影像编号={image_number}")
            return error_response(msg="眼底图像不存在", code=404)

        log.info(f"根据影像编号查询成功: {image_number}")
        return success_response(
            data=FundusImageResponse.model_validate(image).model_dump()
        )

    except Exception as e:
        log.error(f"根据影像编号查询失败: {str(e)}")
        return error_response(msg=f"查询眼底图像失败: {str(e)}", code=500)


@router.put("/{image_id}", response_model=ResponseModel, summary="更新眼底图像")
async def update_fundus_image(
    image_id: int,
    image_update: FundusImageUpdate,
    session: Session = Depends(get_db)
):
    """
    更新眼底图像信息

    - **image_id**: 图像ID
    - 只更新提供的字段，未提供的字段保持不变
    """
    try:
        # 查询图像
        db_image = session.query(FundusImage).filter(
            FundusImage.id == image_id,
            FundusImage.deleted_at.is_(None)
        ).first()

        if not db_image:
            log.warning(f"眼底图像不存在: ID={image_id}")
            return error_response(msg="眼底图像不存在", code=404)

        # 更新字段
        update_data = image_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_image, field, value)

        # 更新时间
        db_image.updated_at = datetime.now()

        session.commit()
        session.refresh(db_image)

        log.info(f"更新眼底图像成功: ID={image_id}")
        return success_response(
            data=FundusImageResponse.model_validate(db_image).model_dump(),
            msg="眼底图像更新成功"
        )

    except Exception as e:
        session.rollback()
        log.error(f"更新眼底图像失败: {str(e)}")
        return error_response(msg=f"更新眼底图像失败: {str(e)}", code=500)


@router.delete("/{image_id}", response_model=ResponseModel, summary="删除单个眼底图像")
async def delete_fundus_image(
    image_id: int,
    session: Session = Depends(get_db)
):
    """
    软删除单个眼底图像

    - **image_id**: 图像ID
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        image = session.query(FundusImage).filter(
            FundusImage.id == image_id,
            FundusImage.deleted_at.is_(None)
        ).first()

        if not image:
            log.warning(f"眼底图像不存在: ID={image_id}")
            return error_response(msg="眼底图像不存在", code=404)

        # 软删除
        image.deleted_at = datetime.now()
        session.commit()

        log.info(f"删除眼底图像成功: ID={image_id}")
        return success_response(msg="眼底图像删除成功")

    except Exception as e:
        session.rollback()
        log.error(f"删除眼底图像失败: {str(e)}")
        return error_response(msg=f"删除眼底图像失败: {str(e)}", code=500)


@router.delete("/", response_model=ResponseModel, summary="批量删除眼底图像")
async def batch_delete_fundus_images(
    delete_request: FundusImageDeleteRequest,
    session: Session = Depends(get_db)
):
    """
    批量软删除眼底图像

    - **ids**: 要删除的图像ID列表
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        image_ids = delete_request.ids

        # 查询要删除的图像
        images = session.query(FundusImage).filter(
            FundusImage.id.in_(image_ids),
            FundusImage.deleted_at.is_(None)
        ).all()

        if not images:
            log.warning("没有找到要删除的眼底图像")
            return error_response(msg="没有找到要删除的眼底图像", code=404)

        # 批量软删除
        deleted_count = 0
        deleted_ids = []

        for image in images:
            image.deleted_at = datetime.now()
            deleted_ids.append(image.id)
            deleted_count += 1

        skipped_count = len(image_ids) - deleted_count

        session.commit()

        log.info(f"批量删除眼底图像成功: 删除数={deleted_count}, 跳过数={skipped_count}")
        return success_response(msg=f"成功删除 {deleted_count} 条眼底图像", data={
            "deleted_count": deleted_count,
            "skipped_count": skipped_count,
            "deleted_ids": deleted_ids
        })

    except Exception as e:
        session.rollback()
        log.error(f"批量删除眼底图像失败: {str(e)}")
        return error_response(msg=f"批量删除眼底图像失败: {str(e)}", code=500)
