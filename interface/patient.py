"""
患者管理API - RESTful风格
支持：单个查询、分页查询、创建、更新、批量删除
"""
from typing import Optional, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field as PydanticField

from models.patient import Patient
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class PatientCreate(BaseModel):
    """患者创建模型"""
    patient_id: str = PydanticField(..., min_length=1, max_length=50, description="患者编号")
    name: str = PydanticField(..., min_length=1, max_length=100, description="患者姓名")
    gender: Optional[str] = PydanticField(None, pattern='^(male|female|other)$', description="性别")
    birth_date: Optional[date] = PydanticField(None, description="出生日期")
    phone: Optional[str] = PydanticField(None, max_length=20, description="联系电话")
    email: Optional[EmailStr] = PydanticField(None, description="邮箱")
    address: Optional[str] = PydanticField(None, description="地址")
    emergency_contact: Optional[str] = PydanticField(None, max_length=100, description="紧急联系人")
    emergency_phone: Optional[str] = PydanticField(None, max_length=20, description="紧急联系人电话")
    medical_history: Optional[str] = PydanticField(None, description="病史")
    allergies: Optional[str] = PydanticField(None, description="过敏史")
    current_medications: Optional[str] = PydanticField(None, description="当前用药")
    insurance_info: Optional[dict] = PydanticField(None, description="医保信息")
    status: str = PydanticField(default='active', pattern='^(active|inactive|deceased)$', description="状态")
    created_by: Optional[int] = PydanticField(None, description="创建人ID")


class PatientUpdate(BaseModel):
    """患者更新模型"""
    name: Optional[str] = PydanticField(None, min_length=1, max_length=100, description="患者姓名")
    gender: Optional[str] = PydanticField(None, pattern='^(male|female|other)$', description="性别")
    birth_date: Optional[date] = PydanticField(None, description="出生日期")
    phone: Optional[str] = PydanticField(None, max_length=20, description="联系电话")
    email: Optional[EmailStr] = PydanticField(None, description="邮箱")
    address: Optional[str] = PydanticField(None, description="地址")
    emergency_contact: Optional[str] = PydanticField(None, max_length=100, description="紧急联系人")
    emergency_phone: Optional[str] = PydanticField(None, max_length=20, description="紧急联系人电话")
    medical_history: Optional[str] = PydanticField(None, description="病史")
    allergies: Optional[str] = PydanticField(None, description="过敏史")
    current_medications: Optional[str] = PydanticField(None, description="当前用药")
    insurance_info: Optional[dict] = PydanticField(None, description="医保信息")
    status: Optional[str] = PydanticField(None, pattern='^(active|inactive|deceased)$', description="状态")
    updated_by: Optional[int] = PydanticField(None, description="更新人ID")


class PatientResponse(BaseModel):
    """患者响应模型"""
    id: int
    patient_id: str
    name: str
    gender: Optional[str] = None
    birth_date: Optional[date] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    medical_history: Optional[str] = None
    allergies: Optional[str] = None
    current_medications: Optional[str] = None
    insurance_info: Optional[dict] = None
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class PatientDeleteRequest(BaseModel):
    """批量删除患者请求模型"""
    patient_ids: List[int] = PydanticField(..., min_length=1, description="要删除的患者ID列表")
    deleted_by: Optional[int] = PydanticField(None, description="删除操作人ID")


# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建新患者")
def create_patient(patient_data: PatientCreate, db: Session = Depends(get_db)):
    """
    创建新患者
    
    - **patient_id**: 患者编号（唯一）
    - **name**: 患者姓名
    - **gender**: 性别 (male/female/other)
    - **birth_date**: 出生日期
    - **phone**: 联系电话
    - **email**: 邮箱
    - **status**: 状态 (active/inactive/deceased)
    """
    log.info(f"创建新患者: patient_id={patient_data.patient_id}, name={patient_data.name}")
    
    # 检查患者编号是否已存在
    existing_patient = db.query(Patient).filter(
        Patient.patient_id == patient_data.patient_id,
        Patient.deleted_at.is_(None)
    ).first()
    if existing_patient:
        log.warning(f"患者编号已存在: {patient_data.patient_id}")
        return error_response(code=400, msg="患者编号已存在")
    
    # 创建患者对象
    new_patient = Patient(**patient_data.model_dump())
    db.add(new_patient)
    db.commit()
    db.refresh(new_patient)
    
    log.info(f"成功创建患者: id={new_patient.id}, patient_id={new_patient.patient_id}")
    
    # 返回创建的患者信息
    patient_response = PatientResponse.model_validate(new_patient)
    return success_response(data=patient_response.model_dump())


@router.get("/{patient_id}", response_model=ResponseModel, summary="根据ID获取单个患者")
def get_patient(patient_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取单个患者信息（排除已软删除的患者）
    
    - **patient_id**: 患者内部ID
    """
    log.debug(f"查询患者: id={patient_id}")
    
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.deleted_at.is_(None)
    ).first()
    
    if not patient:
        log.warning(f"患者未找到: id={patient_id}")
        return error_response(code=404, msg="患者未找到")
    
    log.debug(f"成功查询患者: id={patient.id}, name={patient.name}")
    
    patient_response = PatientResponse.model_validate(patient)
    return success_response(data=patient_response.model_dump())


@router.get("/", response_model=ResponseModel, summary="分页查询患者列表")
def list_patients(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    status: Optional[str] = Query(None, description="状态筛选 (active/inactive/deceased)"),
    gender: Optional[str] = Query(None, description="性别筛选 (male/female/other)"),
    name: Optional[str] = Query(None, description="姓名模糊查询"),
    patient_id: Optional[str] = Query(None, description="患者编号模糊查询"),
    db: Session = Depends(get_db)
):
    """
    分页查询患者列表（排除已软删除的患者）
    
    支持的筛选条件：
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量（1-100）
    - **status**: 状态筛选
    - **gender**: 性别筛选
    - **name**: 姓名模糊查询
    - **patient_id**: 患者编号模糊查询
    """
    log.debug(f"分页查询患者: page={page}, page_size={page_size}, status={status}, gender={gender}")
    
    offset = (page - 1) * page_size
    
    # 构建查询，排除软删除的患者
    query = db.query(Patient).filter(Patient.deleted_at.is_(None))
    
    # 添加筛选条件
    if status:
        query = query.filter(Patient.status == status)
    if gender:
        query = query.filter(Patient.gender == gender)
    if name:
        query = query.filter(Patient.name.like(f"%{name}%"))
    if patient_id:
        query = query.filter(Patient.patient_id.like(f"%{patient_id}%"))
    
    # 获取总数和分页数据
    total = query.count()
    patients = query.order_by(Patient.created_at.desc()).offset(offset).limit(page_size).all()
    
    log.debug(f"查询到 {total} 个患者，当前页 {len(patients)} 个")
    
    # 转换为响应模型列表
    patients_response = [PatientResponse.model_validate(patient).model_dump() for patient in patients]
    
    return success_response(data={
        "patients": patients_response,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": (total + page_size - 1) // page_size
        }
    })


@router.put("/{patient_id}", response_model=ResponseModel, summary="更新患者信息")
def update_patient(patient_id: int, patient_data: PatientUpdate, db: Session = Depends(get_db)):
    """
    更新患者信息（排除已软删除的患者）
    
    - **patient_id**: 患者内部ID
    - 只更新提供的字段，未提供的字段保持不变
    """
    log.info(f"更新患者信息: id={patient_id}")
    
    # 查找患者（排除软删除）
    patient = db.query(Patient).filter(
        Patient.id == patient_id,
        Patient.deleted_at.is_(None)
    ).first()
    
    if not patient:
        log.warning(f"患者未找到: id={patient_id}")
        return error_response(code=404, msg="患者未找到")
    
    # 更新字段（只更新提供的字段）
    update_data = patient_data.model_dump(exclude_unset=True)
    if not update_data:
        log.warning(f"没有提供任何更新字段: id={patient_id}")
        return error_response(code=400, msg="没有提供任何更新字段")
    
    for key, value in update_data.items():
        setattr(patient, key, value)
    
    # updated_at 会由数据库触发器自动更新
    db.commit()
    db.refresh(patient)
    
    log.info(f"成功更新患者: id={patient.id}, name={patient.name}")
    
    # 返回更新后的患者信息
    patient_response = PatientResponse.model_validate(patient)
    return success_response(data=patient_response.model_dump())


@router.delete("/", response_model=ResponseModel, summary="批量删除患者（软删除）")
def delete_patients(delete_request: PatientDeleteRequest, db: Session = Depends(get_db)):
    """
    批量软删除患者
    
    - **patient_ids**: 要删除的患者ID列表
    - **deleted_by**: 删除操作人ID（可选）
    
    注意：这是软删除操作，不会真正删除数据，只是标记为已删除
    """
    log.info(f"批量删除患者: ids={delete_request.patient_ids}, deleted_by={delete_request.deleted_by}")
    
    # 查找未被软删除的患者
    patients = db.query(Patient).filter(
        Patient.id.in_(delete_request.patient_ids),
        Patient.deleted_at.is_(None)
    ).all()
    
    if not patients:
        log.warning(f"未找到可删除的患者: {delete_request.patient_ids}")
        return error_response(code=404, msg="未找到可删除的患者")
    
    # 执行软删除
    deleted_count = 0
    deleted_ids = []
    for patient in patients:
        patient.deleted_at = datetime.now()
        if delete_request.deleted_by:
            patient.updated_by = delete_request.deleted_by
        deleted_count += 1
        deleted_ids.append(patient.id)
    
    db.commit()
    log.info(f"成功软删除 {deleted_count} 个患者: {deleted_ids}")
    
    return success_response(data={
        "deleted_count": deleted_count,
        "deleted_ids": deleted_ids
    })


# ==================== 额外的便捷端点 ====================

@router.get("/by-patient-id/{patient_id}", response_model=ResponseModel, summary="根据患者编号查询")
def get_patient_by_patient_id(patient_id: str, db: Session = Depends(get_db)):
    """
    根据患者编号（patient_id字段）查询患者信息
    
    - **patient_id**: 患者编号（非内部ID）
    """
    log.debug(f"根据患者编号查询: patient_id={patient_id}")
    
    patient = db.query(Patient).filter(
        Patient.patient_id == patient_id,
        Patient.deleted_at.is_(None)
    ).first()
    
    if not patient:
        log.warning(f"患者未找到: patient_id={patient_id}")
        return error_response(code=404, msg="患者未找到")
    
    log.debug(f"成功查询患者: id={patient.id}, patient_id={patient.patient_id}")
    
    patient_response = PatientResponse.model_validate(patient)
    return success_response(data=patient_response.model_dump())
