"""
诊断记录管理API
提供诊断记录的完整CRUD功能，包括：
- 创建诊断记录
- 查询诊断记录（单个查询、翻页查询）
- 更新诊断记录
- 删除诊断记录（单个删除、批量删除，软删除）
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField

from models.diagnosis_record import DiagnosisRecord
from models.examination import Examination
from models.user import User
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log
from utils.jwt_auth import get_current_user_info, require_permission

router = APIRouter()

# ==================== Pydantic 模型定义 ====================

class DiagnosisRecordCreate(BaseModel):
    """诊断记录创建模型"""
    examination_id: int = PydanticField(..., gt=0, description="检查ID")
    doctor_id: int = PydanticField(..., gt=0, description="医生ID")
    diagnosis_type: str = PydanticField(..., description="诊断类型：primary/secondary/differential/final")
    icd_code: Optional[str] = PydanticField(None, max_length=20, description="ICD编码")
    diagnosis_name: str = PydanticField(..., max_length=200, description="诊断名称")
    diagnosis_description: Optional[str] = PydanticField(None, description="诊断描述")
    severity: Optional[str] = PydanticField(None, description="严重程度：mild/moderate/severe")
    laterality: Optional[str] = PydanticField(None, description="侧别：left/right/bilateral/unspecified")
    confidence_level: Optional[str] = PydanticField(None, description="置信度：definite/probable/possible/rule-out")
    supporting_evidence: Optional[str] = PydanticField(None, description="支持证据")
    differential_diagnoses: Optional[List[str]] = PydanticField(None, description="鉴别诊断列表")
    treatment_plan: Optional[str] = PydanticField(None, description="治疗方案")
    prognosis: Optional[str] = PydanticField(None, description="预后")
    diagnosis_date: Optional[datetime] = PydanticField(None, description="诊断日期时间")
    is_active: bool = PydanticField(default=True, description="是否激活")

    class Config:
        json_schema_extra = {
            "example": {
                "examination_id": 1,
                "doctor_id": 2,
                "diagnosis_type": "primary",
                "icd_code": "H35.0",
                "diagnosis_name": "糖尿病视网膜病变",
                "diagnosis_description": "双眼糖尿病视网膜病变，非增殖期",
                "severity": "moderate",
                "laterality": "bilateral",
                "confidence_level": "definite",
                "is_active": True
            }
        }


class DiagnosisRecordUpdate(BaseModel):
    """诊断记录更新模型"""
    examination_id: Optional[int] = PydanticField(None, gt=0, description="检查ID")
    doctor_id: Optional[int] = PydanticField(None, gt=0, description="医生ID")
    diagnosis_type: Optional[str] = PydanticField(None, description="诊断类型")
    icd_code: Optional[str] = PydanticField(None, max_length=20, description="ICD编码")
    diagnosis_name: Optional[str] = PydanticField(None, max_length=200, description="诊断名称")
    diagnosis_description: Optional[str] = PydanticField(None, description="诊断描述")
    severity: Optional[str] = PydanticField(None, description="严重程度")
    laterality: Optional[str] = PydanticField(None, description="侧别")
    confidence_level: Optional[str] = PydanticField(None, description="置信度")
    supporting_evidence: Optional[str] = PydanticField(None, description="支持证据")
    differential_diagnoses: Optional[List[str]] = PydanticField(None, description="鉴别诊断列表")
    treatment_plan: Optional[str] = PydanticField(None, description="治疗方案")
    prognosis: Optional[str] = PydanticField(None, description="预后")
    diagnosis_date: Optional[datetime] = PydanticField(None, description="诊断日期时间")
    is_active: Optional[bool] = PydanticField(None, description="是否激活")

    class Config:
        json_schema_extra = {
            "example": {
                "diagnosis_name": "糖尿病视网膜病变（更新）",
                "severity": "severe",
                "treatment_plan": "激光治疗"
            }
        }


class UserInfo(BaseModel):
    """用户信息模型（用于医生）"""
    id: int
    username: str
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class ExaminationInfo(BaseModel):
    """检查信息模型"""
    id: int
    examination_number: str
    patient_id: int
    
    class Config:
        from_attributes = True


class DiagnosisRecordResponse(BaseModel):
    """诊断记录响应模型"""
    id: int
    examination_id: int
    doctor_id: int
    diagnosis_type: str
    icd_code: Optional[str] = None
    diagnosis_name: str
    diagnosis_description: Optional[str] = None
    severity: Optional[str] = None
    laterality: Optional[str] = None
    confidence_level: Optional[str] = None
    supporting_evidence: Optional[str] = None
    differential_diagnoses: Optional[List[str]] = None
    treatment_plan: Optional[str] = None
    prognosis: Optional[str] = None
    diagnosis_date: Optional[datetime] = None
    is_active: bool
    deleted_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    # 关联信息
    doctor: Optional[UserInfo] = None
    examination: Optional[ExaminationInfo] = None

    class Config:
        from_attributes = True


class DiagnosisRecordDeleteRequest(BaseModel):
    """诊断记录批量删除请求模型"""
    diagnosis_record_ids: List[int] = PydanticField(..., min_length=1, description="要删除的诊断记录ID列表")

# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建诊断记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_CREATE'))])
async def create_diagnosis_record(
    diagnosis_record: DiagnosisRecordCreate,
    session: Session = Depends(get_db)
):
    """
    创建新的诊断记录
    
    - **examination_id**: 检查ID（必填）
    - **doctor_id**: 医生ID（必填）
    - **diagnosis_type**: 诊断类型（primary/secondary/differential/final）
    - **diagnosis_name**: 诊断名称（必填）
    - **diagnosis_date**: 诊断日期时间（可选，默认为当前时间）
    """
    try:
        # 验证检查记录是否存在
        examination = session.query(Examination).filter(
            Examination.id == diagnosis_record.examination_id,
            Examination.deleted_at.is_(None)
        ).first()
        
        if not examination:
            log.warning(f"检查记录不存在: ID={diagnosis_record.examination_id}")
            return error_response(msg="检查记录不存在", code=404)
        
        # 验证医生是否存在
        doctor = session.query(User).filter(User.id == diagnosis_record.doctor_id).first()
        if not doctor:
            log.warning(f"医生不存在: ID={diagnosis_record.doctor_id}")
            return error_response(msg="医生不存在", code=404)
        
        # 将 Pydantic 模型转为字典
        diagnosis_dict = diagnosis_record.model_dump()
        
        # 如果没有提供诊断日期，使用当前时间
        if not diagnosis_dict.get('diagnosis_date'):
            diagnosis_dict['diagnosis_date'] = datetime.now()
        
        # 创建新诊断记录
        db_diagnosis_record = DiagnosisRecord(**diagnosis_dict)
        session.add(db_diagnosis_record)
        session.commit()
        session.refresh(db_diagnosis_record)
        
        log.info(f"成功创建诊断记录: ID={db_diagnosis_record.id}, 诊断名称={db_diagnosis_record.diagnosis_name}")
        return success_response(
            data=DiagnosisRecordResponse.model_validate(db_diagnosis_record).model_dump(),
            msg="诊断记录创建成功"
        )
    
    except Exception as e:
        session.rollback()
        log.error(f"创建诊断记录失败: {str(e)}")
        return error_response(msg=f"创建诊断记录失败: {str(e)}", code=500)


@router.get("/", response_model=ResponseModel, summary="分页查询诊断记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_VIEW'))])
async def get_diagnosis_records(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    examination_id: Optional[int] = Query(None, description="按检查ID筛选"),
    doctor_id: Optional[int] = Query(None, description="按医生ID筛选"),
    diagnosis_type: Optional[str] = Query(None, description="按诊断类型筛选"),
    diagnosis_name: Optional[str] = Query(None, description="按诊断名称模糊查询"),
    icd_code: Optional[str] = Query(None, description="按ICD编码查询"),
    severity: Optional[str] = Query(None, description="按严重程度筛选"),
    laterality: Optional[str] = Query(None, description="按侧别筛选"),
    confidence_level: Optional[str] = Query(None, description="按置信度筛选"),
    is_active: Optional[bool] = Query(None, description="按是否激活筛选"),
    start_date: Optional[datetime] = Query(None, description="开始日期时间"),
    end_date: Optional[datetime] = Query(None, description="结束日期时间"),
    include_deleted: bool = Query(False, description="是否包含已删除记录"),
    session: Session = Depends(get_db)
):
    """
    分页查询诊断记录列表
    
    支持多种筛选条件：
    - 检查ID
    - 医生ID
    - 诊断类型
    - 诊断名称（模糊查询）
    - ICD编码
    - 严重程度
    - 侧别
    - 置信度
    - 是否激活
    - 日期时间范围
    """
    try:
        # 构建基础查询 - 用于计算总数
        count_query = session.query(DiagnosisRecord)
        
        # 应用筛选条件
        if not include_deleted:
            count_query = count_query.filter(DiagnosisRecord.deleted_at.is_(None))
        
        if examination_id:
            count_query = count_query.filter(DiagnosisRecord.examination_id == examination_id)
        
        if doctor_id:
            count_query = count_query.filter(DiagnosisRecord.doctor_id == doctor_id)
        
        if diagnosis_type:
            count_query = count_query.filter(DiagnosisRecord.diagnosis_type == diagnosis_type)
        
        if diagnosis_name:
            count_query = count_query.filter(DiagnosisRecord.diagnosis_name.ilike(f"%{diagnosis_name}%"))
        
        if icd_code:
            count_query = count_query.filter(DiagnosisRecord.icd_code == icd_code)
        
        if severity:
            count_query = count_query.filter(DiagnosisRecord.severity == severity)
        
        if laterality:
            count_query = count_query.filter(DiagnosisRecord.laterality == laterality)
        
        if confidence_level:
            count_query = count_query.filter(DiagnosisRecord.confidence_level == confidence_level)
        
        if is_active is not None:
            count_query = count_query.filter(DiagnosisRecord.is_active == is_active)
        
        if start_date:
            count_query = count_query.filter(DiagnosisRecord.diagnosis_date >= start_date)
        
        if end_date:
            count_query = count_query.filter(DiagnosisRecord.diagnosis_date <= end_date)
        
        # 计算总数
        total = count_query.count()
        
        # 重新构建查询用于分页数据获取
        data_query = session.query(DiagnosisRecord)
        
        # 应用相同的筛选条件
        if not include_deleted:
            data_query = data_query.filter(DiagnosisRecord.deleted_at.is_(None))
        
        if examination_id:
            data_query = data_query.filter(DiagnosisRecord.examination_id == examination_id)
        
        if doctor_id:
            data_query = data_query.filter(DiagnosisRecord.doctor_id == doctor_id)
        
        if diagnosis_type:
            data_query = data_query.filter(DiagnosisRecord.diagnosis_type == diagnosis_type)
        
        if diagnosis_name:
            data_query = data_query.filter(DiagnosisRecord.diagnosis_name.ilike(f"%{diagnosis_name}%"))
        
        if icd_code:
            data_query = data_query.filter(DiagnosisRecord.icd_code == icd_code)
        
        if severity:
            data_query = data_query.filter(DiagnosisRecord.severity == severity)
        
        if laterality:
            data_query = data_query.filter(DiagnosisRecord.laterality == laterality)
        
        if confidence_level:
            data_query = data_query.filter(DiagnosisRecord.confidence_level == confidence_level)
        
        if is_active is not None:
            data_query = data_query.filter(DiagnosisRecord.is_active == is_active)
        
        if start_date:
            data_query = data_query.filter(DiagnosisRecord.diagnosis_date >= start_date)
        
        if end_date:
            data_query = data_query.filter(DiagnosisRecord.diagnosis_date <= end_date)
        
        # 分页
        offset = (page - 1) * page_size
        diagnosis_records = data_query.order_by(
            DiagnosisRecord.diagnosis_date.desc(), 
            DiagnosisRecord.id.desc()
        ).offset(offset).limit(page_size).all()
        
        # 转换为响应模型，并添加关联信息
        diagnosis_list = []
        for record in diagnosis_records:
            record_dict = DiagnosisRecordResponse.model_validate(record).model_dump()
            
            # 查询关联的医生
            if record.doctor_id:
                doctor = session.query(User).filter(User.id == record.doctor_id).first()
                if doctor:
                    record_dict['doctor'] = UserInfo.model_validate(doctor).model_dump()
            
            # 查询关联的检查
            if record.examination_id:
                examination = session.query(Examination).filter(
                    Examination.id == record.examination_id
                ).first()
                if examination:
                    record_dict['examination'] = ExaminationInfo.model_validate(examination).model_dump()
            
            diagnosis_list.append(record_dict)
        
        log.info(f"查询诊断记录列表成功: 页码={page}, 每页={page_size}, 总数={total}")
        return success_response(data={
            "items": diagnosis_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        })
    
    except Exception as e:
        log.error(f"查询诊断记录列表失败: {str(e)}")
        return error_response(msg=f"查询诊断记录列表失败: {str(e)}", code=500)


@router.get("/{diagnosis_record_id}", response_model=ResponseModel, summary="查询单个诊断记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_VIEW'))])
async def get_diagnosis_record(
    diagnosis_record_id: int,
    session: Session = Depends(get_db)
):
    """
    根据ID查询单个诊断记录
    
    - **diagnosis_record_id**: 诊断记录ID
    """
    try:
        diagnosis_record = session.query(DiagnosisRecord).filter(
            DiagnosisRecord.id == diagnosis_record_id,
            DiagnosisRecord.deleted_at.is_(None)
        ).first()
        
        if not diagnosis_record:
            log.warning(f"诊断记录不存在: ID={diagnosis_record_id}")
            return error_response(msg="诊断记录不存在", code=404)
        
        # 构建响应数据，包含关联信息
        record_dict = DiagnosisRecordResponse.model_validate(diagnosis_record).model_dump()
        
        # 查询关联的医生
        if diagnosis_record.doctor_id:
            doctor = session.query(User).filter(User.id == diagnosis_record.doctor_id).first()
            if doctor:
                record_dict['doctor'] = UserInfo.model_validate(doctor).model_dump()
        
        # 查询关联的检查
        if diagnosis_record.examination_id:
            examination = session.query(Examination).filter(
                Examination.id == diagnosis_record.examination_id
            ).first()
            if examination:
                record_dict['examination'] = ExaminationInfo.model_validate(examination).model_dump()
        
        log.info(f"查询诊断记录成功: ID={diagnosis_record_id}")
        return success_response(data=record_dict)
    
    except Exception as e:
        log.error(f"查询诊断记录失败: {str(e)}")
        return error_response(msg=f"查询诊断记录失败: {str(e)}", code=500)


@router.put("/{diagnosis_record_id}", response_model=ResponseModel, summary="更新诊断记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_EDIT'))])
async def update_diagnosis_record(
    diagnosis_record_id: int,
    diagnosis_record_update: DiagnosisRecordUpdate,
    session: Session = Depends(get_db)
):
    """
    更新诊断记录信息
    
    - **diagnosis_record_id**: 诊断记录ID
    - 只更新提供的字段，未提供的字段保持不变
    """
    try:
        # 查询诊断记录
        db_diagnosis_record = session.query(DiagnosisRecord).filter(
            DiagnosisRecord.id == diagnosis_record_id,
            DiagnosisRecord.deleted_at.is_(None)
        ).first()
        
        if not db_diagnosis_record:
            log.warning(f"诊断记录不存在: ID={diagnosis_record_id}")
            return error_response(msg="诊断记录不存在", code=404)
        
        # 如果要更新检查ID，验证检查记录是否存在
        if diagnosis_record_update.examination_id and diagnosis_record_update.examination_id != db_diagnosis_record.examination_id:
            examination = session.query(Examination).filter(
                Examination.id == diagnosis_record_update.examination_id,
                Examination.deleted_at.is_(None)
            ).first()
            if not examination:
                log.warning(f"检查记录不存在: ID={diagnosis_record_update.examination_id}")
                return error_response(msg="检查记录不存在", code=404)
        
        # 如果要更新医生ID，验证医生是否存在
        if diagnosis_record_update.doctor_id and diagnosis_record_update.doctor_id != db_diagnosis_record.doctor_id:
            doctor = session.query(User).filter(User.id == diagnosis_record_update.doctor_id).first()
            if not doctor:
                log.warning(f"医生不存在: ID={diagnosis_record_update.doctor_id}")
                return error_response(msg="医生不存在", code=404)
        
        # 更新字段
        update_data = diagnosis_record_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_diagnosis_record, field, value)
        
        # 更新时间
        db_diagnosis_record.updated_at = datetime.now()
        
        session.commit()
        session.refresh(db_diagnosis_record)
        
        log.info(f"更新诊断记录成功: ID={diagnosis_record_id}")
        return success_response(
            data=DiagnosisRecordResponse.model_validate(db_diagnosis_record).model_dump(),
            msg="诊断记录更新成功"
        )
    
    except Exception as e:
        session.rollback()
        log.error(f"更新诊断记录失败: {str(e)}")
        return error_response(msg=f"更新诊断记录失败: {str(e)}", code=500)


@router.delete("/{diagnosis_record_id}", response_model=ResponseModel, summary="删除单个诊断记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_DELETE'))])
async def delete_diagnosis_record(
    diagnosis_record_id: int,
    session: Session = Depends(get_db)
):
    """
    软删除单个诊断记录
    
    - **diagnosis_record_id**: 诊断记录ID
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        diagnosis_record = session.query(DiagnosisRecord).filter(
            DiagnosisRecord.id == diagnosis_record_id,
            DiagnosisRecord.deleted_at.is_(None)
        ).first()
        
        if not diagnosis_record:
            log.warning(f"诊断记录不存在: ID={diagnosis_record_id}")
            return error_response(msg="诊断记录不存在", code=404)
        
        # 软删除
        diagnosis_record.deleted_at = datetime.now()
        session.commit()
        
        log.info(f"删除诊断记录成功: ID={diagnosis_record_id}")
        return success_response(msg="诊断记录删除成功")
    
    except Exception as e:
        session.rollback()
        log.error(f"删除诊断记录失败: {str(e)}")
        return error_response(msg=f"删除诊断记录失败: {str(e)}", code=500)


@router.delete("/", response_model=ResponseModel, summary="批量删除诊断记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('DIAGNOSIS_DELETE'))])
async def batch_delete_diagnosis_records(
    delete_request: DiagnosisRecordDeleteRequest,
    session: Session = Depends(get_db)
):
    """
    批量软删除诊断记录
    
    - **diagnosis_record_ids**: 要删除的诊断记录ID列表
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        diagnosis_record_ids = delete_request.diagnosis_record_ids
        
        # 查询要删除的诊断记录
        diagnosis_records = session.query(DiagnosisRecord).filter(
            DiagnosisRecord.id.in_(diagnosis_record_ids),
            DiagnosisRecord.deleted_at.is_(None)
        ).all()
        
        if not diagnosis_records:
            log.warning("没有找到要删除的诊断记录")
            return error_response(msg="没有找到要删除的诊断记录", code=404)
        
        # 批量软删除
        deleted_count = 0
        skipped_count = 0
        deleted_ids = []
        
        for diagnosis_record in diagnosis_records:
            diagnosis_record.deleted_at = datetime.now()
            deleted_ids.append(diagnosis_record.id)
            deleted_count += 1
        
        skipped_count = len(diagnosis_record_ids) - deleted_count
        
        session.commit()
        
        log.info(f"批量删除诊断记录成功: 删除数={deleted_count}, 跳过数={skipped_count}")
        return success_response(msg=f"成功删除 {deleted_count} 条诊断记录", data={
            "deleted_count": deleted_count,
            "skipped_count": skipped_count,
            "deleted_ids": deleted_ids
        })
    
    except Exception as e:
        session.rollback()
        log.error(f"批量删除诊断记录失败: {str(e)}")
        return error_response(msg=f"批量删除诊断记录失败: {str(e)}", code=500)
