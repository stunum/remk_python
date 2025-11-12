"""
AI诊断信息管理API
提供AI诊断结果的完整CRUD功能，包括：
- 创建AI诊断记录
- 查询AI诊断（单个查询、分页查询、按图像ID查询）
- 更新AI诊断信息
- 删除AI诊断（单个删除、批量删除，软删除）
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField

from models.ai_diagnosis import AIDiagnosis
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log
from utils.jwt_auth import get_current_user_info, require_permission

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class AIDiagnosisCreate(BaseModel):
    """AI诊断创建模型"""
    image_id: int = PydanticField(..., gt=0, description="图像ID")
    ai_model_name: str = PydanticField(..., min_length=1, max_length=100, description="AI模型名称")
    ai_model_version: Optional[str] = PydanticField(None, max_length=50, description="AI模型版本")
    diagnosis_result: dict = PydanticField(..., description="诊断结果（JSON）")
    confidence_score: Optional[Decimal] = PydanticField(None, ge=0, le=1, description="置信度分数（0-1）")
    processing_time_ms: Optional[int] = PydanticField(None, ge=0, description="处理时间（毫秒）")
    severity_level: Optional[str] = PydanticField(
        None, 
        description="严重程度：normal/mild/moderate/severe/critical"
    )
    risk_assessment: Optional[str] = PydanticField(None, description="风险评估")
    recommended_actions: Optional[str] = PydanticField(None, description="推荐行动")
    diagnostic_markers: Optional[dict] = PydanticField(None, description="诊断标记（JSON）")
    processing_status: str = PydanticField(
        default='completed', 
        description="处理状态：pending/processing/completed/failed/timeout"
    )
    error_message: Optional[str] = PydanticField(None, description="错误消息")
    reviewed_by: Optional[int] = PydanticField(None, gt=0, description="审核人ID")
    review_status: str = PydanticField(
        default='pending', 
        description="审核状态：pending/approved/rejected/modified"
    )
    review_comments: Optional[str] = PydanticField(None, description="审核评论")

    class Config:
        json_schema_extra = {
            "example": {
                "image_id": 1,
                "ai_model_name": "RetinaNet_v1.0",
                "ai_model_version": "1.0.0",
                "diagnosis_result": {
                    "disease": "diabetic_retinopathy",
                    "stage": "mild",
                    "findings": ["microaneurysms", "hemorrhages"]
                },
                "confidence_score": 0.95,
                "processing_time_ms": 1250,
                "severity_level": "mild",
                "risk_assessment": "低风险，建议定期复查",
                "recommended_actions": "3个月后复查",
                "diagnostic_markers": {
                    "microaneurysms": 5,
                    "hemorrhages": 2
                },
                "processing_status": "completed",
                "review_status": "pending"
            }
        }


class AIDiagnosisUpdate(BaseModel):
    """AI诊断更新模型"""
    ai_model_name: Optional[str] = PydanticField(None, min_length=1, max_length=100, description="AI模型名称")
    ai_model_version: Optional[str] = PydanticField(None, max_length=50, description="AI模型版本")
    diagnosis_result: Optional[dict] = PydanticField(None, description="诊断结果（JSON）")
    confidence_score: Optional[Decimal] = PydanticField(None, ge=0, le=1, description="置信度分数（0-1）")
    processing_time_ms: Optional[int] = PydanticField(None, ge=0, description="处理时间（毫秒）")
    severity_level: Optional[str] = PydanticField(
        None, 
        description="严重程度：normal/mild/moderate/severe/critical"
    )
    risk_assessment: Optional[str] = PydanticField(None, description="风险评估")
    recommended_actions: Optional[str] = PydanticField(None, description="推荐行动")
    diagnostic_markers: Optional[dict] = PydanticField(None, description="诊断标记（JSON）")
    processing_status: Optional[str] = PydanticField(
        None, 
        description="处理状态：pending/processing/completed/failed/timeout"
    )
    error_message: Optional[str] = PydanticField(None, description="错误消息")
    reviewed_by: Optional[int] = PydanticField(None, gt=0, description="审核人ID")
    review_status: Optional[str] = PydanticField(
        None, 
        description="审核状态：pending/approved/rejected/modified"
    )
    review_comments: Optional[str] = PydanticField(None, description="审核评论")

    class Config:
        json_schema_extra = {
            "example": {
                "review_status": "approved",
                "review_comments": "诊断结果准确，同意AI诊断",
                "reviewed_by": 1
            }
        }


class AIDiagnosisResponse(BaseModel):
    """AI诊断响应模型"""
    id: int
    image_id: int
    ai_model_name: str
    ai_model_version: Optional[str]
    diagnosis_result: dict
    confidence_score: Optional[Decimal]
    processing_time_ms: Optional[int]
    severity_level: Optional[str]
    risk_assessment: Optional[str]
    recommended_actions: Optional[str]
    diagnostic_markers: Optional[dict]
    processing_status: str
    error_message: Optional[str]
    reviewed_by: Optional[int]
    review_status: str
    review_comments: Optional[str]
    reviewed_at: Optional[datetime]
    deleted_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AIDiagnosisDeleteRequest(BaseModel):
    """AI诊断批量删除请求模型"""
    ids: List[int] = PydanticField(..., min_length=1, description="要删除的诊断ID列表")

    class Config:
        json_schema_extra = {
            "example": {
                "ids": [1, 2, 3]
            }
        }


# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建AI诊断记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_CREATE'))])
async def create_ai_diagnosis(
    diagnosis: AIDiagnosisCreate,
    session: Session = Depends(get_db)
):
    """
    创建新的AI诊断记录

    - **image_id**: 图像ID
    - **ai_model_name**: AI模型名称
    - **diagnosis_result**: 诊断结果（JSON格式）
    - **processing_status**: 处理状态（默认：completed）
    - **review_status**: 审核状态（默认：pending）
    """
    try:
        # 创建新诊断记录
        db_diagnosis = AIDiagnosis(**diagnosis.model_dump())
        session.add(db_diagnosis)
        session.commit()
        session.refresh(db_diagnosis)

        log.info(f"成功创建AI诊断记录: ID={db_diagnosis.id}, 图像ID={db_diagnosis.image_id}")
        return success_response(
            data=AIDiagnosisResponse.model_validate(db_diagnosis).model_dump(),
            msg="AI诊断记录创建成功"
        )

    except Exception as e:
        session.rollback()
        log.error(f"创建AI诊断记录失败: {str(e)}")
        return error_response(msg=f"创建AI诊断记录失败: {str(e)}", code=500)


@router.get("/", response_model=ResponseModel, summary="分页查询AI诊断", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_VIEW'))])
async def get_ai_diagnoses(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    image_id: Optional[int] = Query(None, description="按图像ID筛选"),
    ai_model_name: Optional[str] = Query(None, description="按AI模型名称筛选"),
    processing_status: Optional[str] = Query(None, description="按处理状态筛选"),
    review_status: Optional[str] = Query(None, description="按审核状态筛选"),
    severity_level: Optional[str] = Query(None, description="按严重程度筛选"),
    reviewed_by: Optional[int] = Query(None, description="按审核人ID筛选"),
    include_deleted: bool = Query(False, description="是否包含已删除记录"),
    session: Session = Depends(get_db)
):
    """
    分页查询AI诊断列表

    支持多种筛选条件：
    - 图像ID
    - AI模型名称
    - 处理状态
    - 审核状态
    - 严重程度
    - 审核人ID
    """
    try:
        # 构建基础查询 - 用于计算总数
        count_query = session.query(AIDiagnosis)

        # 应用筛选条件
        if not include_deleted:
            count_query = count_query.filter(AIDiagnosis.deleted_at.is_(None))

        if image_id:
            count_query = count_query.filter(AIDiagnosis.image_id == image_id)

        if ai_model_name:
            count_query = count_query.filter(AIDiagnosis.ai_model_name == ai_model_name)

        if processing_status:
            count_query = count_query.filter(AIDiagnosis.processing_status == processing_status)

        if review_status:
            count_query = count_query.filter(AIDiagnosis.review_status == review_status)

        if severity_level:
            count_query = count_query.filter(AIDiagnosis.severity_level == severity_level)

        if reviewed_by:
            count_query = count_query.filter(AIDiagnosis.reviewed_by == reviewed_by)

        # 计算总数
        total = count_query.count()

        # 重新构建查询用于分页数据获取
        data_query = session.query(AIDiagnosis)

        # 应用相同的筛选条件
        if not include_deleted:
            data_query = data_query.filter(AIDiagnosis.deleted_at.is_(None))

        if image_id:
            data_query = data_query.filter(AIDiagnosis.image_id == image_id)

        if ai_model_name:
            data_query = data_query.filter(AIDiagnosis.ai_model_name == ai_model_name)

        if processing_status:
            data_query = data_query.filter(AIDiagnosis.processing_status == processing_status)

        if review_status:
            data_query = data_query.filter(AIDiagnosis.review_status == review_status)

        if severity_level:
            data_query = data_query.filter(AIDiagnosis.severity_level == severity_level)

        if reviewed_by:
            data_query = data_query.filter(AIDiagnosis.reviewed_by == reviewed_by)

        # 分页
        offset = (page - 1) * page_size
        diagnoses = data_query.order_by(AIDiagnosis.created_at.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()

        # 转换为响应模型
        diagnosis_list = [AIDiagnosisResponse.model_validate(
            diag).model_dump() for diag in diagnoses]

        log.info(f"查询AI诊断列表成功: 页码={page}, 每页={page_size}, 总数={total}")
        return success_response(data={
            "items": diagnosis_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        })

    except Exception as e:
        log.error(f"查询AI诊断列表失败: {str(e)}")
        return error_response(msg=f"查询AI诊断列表失败: {str(e)}", code=500)


@router.get("/{diagnosis_id}", response_model=ResponseModel, summary="查询单个AI诊断", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_VIEW'))])
async def get_ai_diagnosis(
    diagnosis_id: int,
    session: Session = Depends(get_db)
):
    """
    根据ID查询单个AI诊断记录

    - **diagnosis_id**: 诊断ID
    """
    try:
        diagnosis = session.query(AIDiagnosis).filter(
            AIDiagnosis.id == diagnosis_id,
            AIDiagnosis.deleted_at.is_(None)
        ).first()

        if not diagnosis:
            log.warning(f"AI诊断不存在: ID={diagnosis_id}")
            return error_response(msg="AI诊断不存在", code=404)

        log.info(f"查询AI诊断成功: ID={diagnosis_id}")
        return success_response(
            data=AIDiagnosisResponse.model_validate(diagnosis).model_dump()
        )

    except Exception as e:
        log.error(f"查询AI诊断失败: {str(e)}")
        return error_response(msg=f"查询AI诊断失败: {str(e)}", code=500)


@router.get("/by-image/{image_id}", response_model=ResponseModel, summary="根据图像ID查询AI诊断", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_VIEW'))])
async def get_ai_diagnoses_by_image(
    image_id: int,
    include_deleted: bool = Query(False, description="是否包含已删除记录"),
    session: Session = Depends(get_db)
):
    """
    根据图像ID查询该图像的所有AI诊断记录

    - **image_id**: 图像ID
    """
    try:
        query = session.query(AIDiagnosis).filter(AIDiagnosis.image_id == image_id)

        if not include_deleted:
            query = query.filter(AIDiagnosis.deleted_at.is_(None))

        diagnoses = query.order_by(AIDiagnosis.created_at.desc()).all()

        if not diagnoses:
            log.info(f"图像ID={image_id}没有找到AI诊断记录")
            return success_response(
                data={"items": [], "total": 0},
                msg="未找到AI诊断记录"
            )

        # 转换为响应模型
        diagnosis_list = [AIDiagnosisResponse.model_validate(
            diag).model_dump() for diag in diagnoses]

        log.info(f"根据图像ID查询AI诊断成功: 图像ID={image_id}, 记录数={len(diagnosis_list)}")
        return success_response(data={
            "items": diagnosis_list,
            "total": len(diagnosis_list)
        })

    except Exception as e:
        log.error(f"根据图像ID查询AI诊断失败: {str(e)}")
        return error_response(msg=f"查询AI诊断失败: {str(e)}", code=500)


@router.put("/{diagnosis_id}", response_model=ResponseModel, summary="更新AI诊断", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_EDIT'))])
async def update_ai_diagnosis(
    diagnosis_id: int,
    diagnosis_update: AIDiagnosisUpdate,
    session: Session = Depends(get_db)
):
    """
    更新AI诊断信息

    - **diagnosis_id**: 诊断ID
    - 只更新提供的字段，未提供的字段保持不变
    - 如果更新审核相关字段，会自动设置 reviewed_at 时间
    """
    try:
        # 查询诊断记录
        db_diagnosis = session.query(AIDiagnosis).filter(
            AIDiagnosis.id == diagnosis_id,
            AIDiagnosis.deleted_at.is_(None)
        ).first()

        if not db_diagnosis:
            log.warning(f"AI诊断不存在: ID={diagnosis_id}")
            return error_response(msg="AI诊断不存在", code=404)

        # 更新字段
        update_data = diagnosis_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_diagnosis, field, value)

        # 如果更新了审核相关字段，设置审核时间
        if 'review_status' in update_data or 'reviewed_by' in update_data or 'review_comments' in update_data:
            if db_diagnosis.reviewed_at is None and db_diagnosis.review_status != 'pending':
                db_diagnosis.reviewed_at = datetime.now()

        # 更新时间
        db_diagnosis.updated_at = datetime.now()

        session.commit()
        session.refresh(db_diagnosis)

        log.info(f"更新AI诊断成功: ID={diagnosis_id}")
        return success_response(
            data=AIDiagnosisResponse.model_validate(db_diagnosis).model_dump(),
            msg="AI诊断更新成功"
        )

    except Exception as e:
        session.rollback()
        log.error(f"更新AI诊断失败: {str(e)}")
        return error_response(msg=f"更新AI诊断失败: {str(e)}", code=500)


@router.delete("/{diagnosis_id}", response_model=ResponseModel, summary="删除单个AI诊断", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_DELETE'))])
async def delete_ai_diagnosis(
    diagnosis_id: int,
    session: Session = Depends(get_db)
):
    """
    软删除单个AI诊断

    - **diagnosis_id**: 诊断ID
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        diagnosis = session.query(AIDiagnosis).filter(
            AIDiagnosis.id == diagnosis_id,
            AIDiagnosis.deleted_at.is_(None)
        ).first()

        if not diagnosis:
            log.warning(f"AI诊断不存在: ID={diagnosis_id}")
            return error_response(msg="AI诊断不存在", code=404)

        # 软删除
        diagnosis.deleted_at = datetime.now()
        session.commit()

        log.info(f"删除AI诊断成功: ID={diagnosis_id}")
        return success_response(msg="AI诊断删除成功")

    except Exception as e:
        session.rollback()
        log.error(f"删除AI诊断失败: {str(e)}")
        return error_response(msg=f"删除AI诊断失败: {str(e)}", code=500)


@router.delete("/", response_model=ResponseModel, summary="批量删除AI诊断", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_DELETE'))])
async def batch_delete_ai_diagnoses(
    delete_request: AIDiagnosisDeleteRequest,
    session: Session = Depends(get_db)
):
    """
    批量软删除AI诊断

    - **ids**: 要删除的诊断ID列表
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        diagnosis_ids = delete_request.ids

        # 查询要删除的诊断记录
        diagnoses = session.query(AIDiagnosis).filter(
            AIDiagnosis.id.in_(diagnosis_ids),
            AIDiagnosis.deleted_at.is_(None)
        ).all()

        if not diagnoses:
            log.warning("没有找到要删除的AI诊断记录")
            return error_response(msg="没有找到要删除的AI诊断记录", code=404)

        # 批量软删除
        deleted_count = 0
        deleted_ids = []

        for diagnosis in diagnoses:
            diagnosis.deleted_at = datetime.now()
            deleted_ids.append(diagnosis.id)
            deleted_count += 1

        skipped_count = len(diagnosis_ids) - deleted_count

        session.commit()

        log.info(f"批量删除AI诊断成功: 删除数={deleted_count}, 跳过数={skipped_count}")
        return success_response(msg=f"成功删除 {deleted_count} 条AI诊断记录", data={
            "deleted_count": deleted_count,
            "skipped_count": skipped_count,
            "deleted_ids": deleted_ids
        })

    except Exception as e:
        session.rollback()
        log.error(f"批量删除AI诊断失败: {str(e)}")
        return error_response(msg=f"批量删除AI诊断失败: {str(e)}", code=500)
