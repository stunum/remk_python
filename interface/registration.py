"""
挂号管理API
提供挂号记录的完整CRUD功能，包括：
- 创建挂号记录
- 查询挂号记录（单个查询、分页查询）
- 更新挂号记录
- 删除挂号记录（单个删除、批量删除，软删除）
"""
from typing import Optional, List
from datetime import datetime, date, time as time_type
from decimal import Decimal
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field as PydanticField

from models.registration import Registration
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log
from utils.jwt_auth import get_current_user_info, require_permission

router = APIRouter()


# ==================== Pydantic 模型定义 ====================

class RegistrationCreate(BaseModel):
    """挂号创建模型"""
    registration_number: str = PydanticField(
        ..., min_length=1, max_length=50, description="挂号编号（唯一）")
    patient_id: int = PydanticField(..., gt=0, description="患者ID")
    examination_type_id: int = PydanticField(..., gt=0, description="检查类型ID")
    doctor_id: Optional[int] = PydanticField(None, gt=0, description="医生ID")
    department: Optional[str] = PydanticField(
        None, max_length=100, description="科室")
    registration_date: date = PydanticField(..., description="挂号日期")
    registration_time: Optional[time_type] = PydanticField(
        None, description="挂号时间")
    scheduled_date: date = PydanticField(..., description="预约日期")
    scheduled_time: Optional[time_type] = PydanticField(
        None, description="预约时间")
    priority: str = PydanticField(
        default="normal", description="优先级：urgent/high/normal/low")
    registration_type: str = PydanticField(
        default="normal", description="挂号类型：emergency/appointment/normal/followup")
    status: str = PydanticField(
        default="unsigned", description="状态：unsigned/checked_in/cancelled")
    registration_fee: Optional[Decimal] = PydanticField(
        None, ge=0, description="挂号费")
    payment_status: str = PydanticField(
        default="unpaid", description="支付状态：unpaid/paid/refunded")
    payment_method: Optional[str] = PydanticField(
        None, max_length=20, description="支付方式")
    chief_complaint: Optional[str] = PydanticField(None, description="主诉")
    present_illness: Optional[str] = PydanticField(None, description="现病史")
    referral_doctor: Optional[str] = PydanticField(
        None, max_length=100, description="转诊医生")
    referral_hospital: Optional[str] = PydanticField(
        None, max_length=200, description="转诊医院")
    notes: Optional[str] = PydanticField(None, description="备注")
    queue_number: Optional[int] = PydanticField(None, ge=0, description="排队号")
    estimated_wait_time: Optional[int] = PydanticField(
        None, ge=0, description="预计等待时间（分钟）")
    created_by: Optional[int] = PydanticField(None, gt=0, description="创建人ID")
    updated_by: Optional[int] = PydanticField(None, gt=0, description="更新人ID")

    class Config:
        json_schema_extra = {
            "example": {
                "registration_number": "REG20250101001",
                "patient_id": 1,
                "examination_type_id": 1,
                "doctor_id": 2,
                "registration_date": "2025-01-15",
                "registration_time": "08:30:00",
                "scheduled_date": "2025-01-15",
                "scheduled_time": "09:00:00",
                "priority": "normal",
                "registration_type": "normal",
                "status": "unsigned",
                "registration_fee": 50.00,
                "payment_status": "paid"
            }
        }


class RegistrationUpdate(BaseModel):
    """挂号更新模型"""
    registration_number: Optional[str] = PydanticField(
        None, min_length=1, max_length=50, description="挂号编号")
    patient_id: Optional[int] = PydanticField(None, gt=0, description="患者ID")
    examination_type_id: Optional[int] = PydanticField(
        None, gt=0, description="检查类型ID")
    doctor_id: Optional[int] = PydanticField(None, gt=0, description="医生ID")
    department: Optional[str] = PydanticField(
        None, max_length=100, description="科室")
    registration_date: Optional[date] = PydanticField(None, description="挂号日期")
    registration_time: Optional[time_type] = PydanticField(
        None, description="挂号时间")
    scheduled_date: Optional[date] = PydanticField(None, description="预约日期")
    scheduled_time: Optional[time_type] = PydanticField(
        None, description="预约时间")
    priority: Optional[str] = PydanticField(
        None, description="优先级：urgent/high/normal/low")
    registration_type: Optional[str] = PydanticField(
        None, description="挂号类型：emergency/appointment/normal/followup")
    status: Optional[str] = PydanticField(
        None, description="状态：unsigned/checked_in/cancelled")
    registration_fee: Optional[Decimal] = PydanticField(
        None, ge=0, description="挂号费")
    payment_status: Optional[str] = PydanticField(
        None, description="支付状态：unpaid/paid/refunded")
    payment_method: Optional[str] = PydanticField(
        None, max_length=20, description="支付方式")
    chief_complaint: Optional[str] = PydanticField(None, description="主诉")
    present_illness: Optional[str] = PydanticField(None, description="现病史")
    referral_doctor: Optional[str] = PydanticField(
        None, max_length=100, description="转诊医生")
    referral_hospital: Optional[str] = PydanticField(
        None, max_length=200, description="转诊医院")
    notes: Optional[str] = PydanticField(None, description="备注")
    check_in_time: Optional[datetime] = PydanticField(None, description="签到时间")
    queue_number: Optional[int] = PydanticField(None, ge=0, description="排队号")
    estimated_wait_time: Optional[int] = PydanticField(
        None, ge=0, description="预计等待时间（分钟）")
    updated_by: Optional[int] = PydanticField(None, gt=0, description="更新人ID")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "checked_in",
                "check_in_time": "2025-01-15T08:45:00",
                "queue_number": 5
            }
        }


class RegistrationResponse(BaseModel):
    """挂号响应模型"""
    id: int
    registration_number: str
    patient_id: int
    examination_type_id: int
    doctor_id: Optional[int]
    department: Optional[str]
    registration_date: date
    registration_time: Optional[time_type]
    scheduled_date: date
    scheduled_time: Optional[time_type]
    priority: str
    registration_type: str
    status: str
    registration_fee: Optional[Decimal]
    payment_status: str
    payment_method: Optional[str]
    chief_complaint: Optional[str]
    present_illness: Optional[str]
    referral_doctor: Optional[str]
    referral_hospital: Optional[str]
    notes: Optional[str]
    check_in_time: Optional[datetime]
    queue_number: Optional[int]
    estimated_wait_time: Optional[int]
    deleted_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]

    class Config:
        from_attributes = True


class RegistrationDeleteRequest(BaseModel):
    """挂号批量删除请求模型"""
    ids: List[int] = PydanticField(..., min_length=1, description="要删除的挂号ID列表")

    class Config:
        json_schema_extra = {
            "example": {
                "ids": [1, 2, 3]
            }
        }


# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建挂号记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('REGISTRATION_CREATE'))])
async def create_registration(
    registration: RegistrationCreate,
    session: Session = Depends(get_db)
):
    """
    创建新的挂号记录

    - **registration_number**: 挂号编号，必须唯一
    - **patient_id**: 患者ID
    - **examination_type_id**: 检查类型ID
    - **registration_date**: 挂号日期
    - **scheduled_date**: 预约日期
    - **status**: 挂号状态（unsigned/checked_in/cancelled）
    """
    try:
        # 检查挂号编号是否已存在
        existing = session.query(Registration).filter(
            Registration.registration_number == registration.registration_number,
            Registration.deleted_at.is_(None)
        ).first()

        if existing:
            log.warning(f"挂号编号已存在: {registration.registration_number}")
            return error_response(msg=f"挂号编号 {registration.registration_number} 已存在", code=400)

        # 创建新挂号记录
        db_registration = Registration(**registration.model_dump())
        session.add(db_registration)
        session.commit()
        session.refresh(db_registration)

        log.info(
            f"成功创建挂号记录: ID={db_registration.id}, 挂号编号={db_registration.registration_number}")
        return success_response(
            data=RegistrationResponse.model_validate(
                db_registration).model_dump(),
            msg="挂号记录创建成功"
        )

    except Exception as e:
        session.rollback()
        log.error(f"创建挂号记录失败: {str(e)}")
        return error_response(msg=f"创建挂号记录失败: {str(e)}", code=500)


@router.get("/", response_model=ResponseModel, summary="分页查询挂号记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('REGISTRATION_VIEW'))])
async def get_registrations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    patient_id: Optional[int] = Query(None, description="按患者ID筛选"),
    doctor_id: Optional[int] = Query(None, description="按医生ID筛选"),
    examination_type_id: Optional[int] = Query(None, description="按检查类型ID筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    registration_type: Optional[str] = Query(None, description="按挂号类型筛选"),
    payment_status: Optional[str] = Query(None, description="按支付状态筛选"),
    priority: Optional[str] = Query(None, description="按优先级筛选"),
    registration_number: Optional[str] = Query(None, description="按挂号编号筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    include_deleted: bool = Query(False, description="是否包含已删除记录"),
    session: Session = Depends(get_db)
):
    """
    分页查询挂号记录列表

    支持多种筛选条件：
    - 患者ID
    - 医生ID
    - 检查类型ID
    - 挂号状态
    - 挂号类型
    - 支付状态
    - 优先级
    - 挂号编号
    - 日期范围
    """
    try:
        # 构建基础查询 - 用于计算总数
        count_query = session.query(Registration)

        # 应用筛选条件
        if not include_deleted:
            count_query = count_query.filter(Registration.deleted_at.is_(None))

        if patient_id:
            count_query = count_query.filter(Registration.patient_id == patient_id)

        if doctor_id:
            count_query = count_query.filter(Registration.doctor_id == doctor_id)

        if examination_type_id:
            count_query = count_query.filter(
                Registration.examination_type_id == examination_type_id)

        if status:
            count_query = count_query.filter(Registration.status == status)

        if registration_type:
            count_query = count_query.filter(
                Registration.registration_type == registration_type)

        if payment_status:
            count_query = count_query.filter(Registration.payment_status == payment_status)

        if priority:
            count_query = count_query.filter(Registration.priority == priority)

        if registration_number:
            count_query = count_query.filter(Registration.registration_number.ilike(
                f"%{registration_number}%"))

        if start_date:
            count_query = count_query.filter(Registration.scheduled_date >= start_date)

        if end_date:
            count_query = count_query.filter(Registration.scheduled_date <= end_date)

        # 计算总数
        total = count_query.count()

        # 重新构建查询用于分页数据获取
        data_query = session.query(Registration)

        # 应用相同的筛选条件
        if not include_deleted:
            data_query = data_query.filter(Registration.deleted_at.is_(None))

        if patient_id:
            data_query = data_query.filter(Registration.patient_id == patient_id)

        if doctor_id:
            data_query = data_query.filter(Registration.doctor_id == doctor_id)

        if examination_type_id:
            data_query = data_query.filter(
                Registration.examination_type_id == examination_type_id)

        if status:
            data_query = data_query.filter(Registration.status == status)

        if registration_type:
            data_query = data_query.filter(
                Registration.registration_type == registration_type)

        if payment_status:
            data_query = data_query.filter(Registration.payment_status == payment_status)

        if priority:
            data_query = data_query.filter(Registration.priority == priority)

        if registration_number:
            data_query = data_query.filter(Registration.registration_number.ilike(
                f"%{registration_number}%"))

        if start_date:
            data_query = data_query.filter(Registration.scheduled_date >= start_date)

        if end_date:
            data_query = data_query.filter(Registration.scheduled_date <= end_date)

        # 分页
        offset = (page - 1) * page_size
        registrations = data_query.order_by(Registration.scheduled_date.desc(), Registration.id.desc())\
            .offset(offset)\
            .limit(page_size)\
            .all()

        # 转换为响应模型
        registration_list = [RegistrationResponse.model_validate(
            reg).model_dump() for reg in registrations]

        log.info(f"查询挂号记录列表成功: 页码={page}, 每页={page_size}, 总数={total}")
        return success_response(data={
            "items": registration_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        })

    except Exception as e:
        log.error(f"查询挂号记录列表失败: {str(e)}")
        return error_response(msg=f"查询挂号记录列表失败: {str(e)}", code=500)


@router.get("/{registration_id}", response_model=ResponseModel, summary="查询单个挂号记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('REGISTRATION_VIEW'))])
async def get_registration(
    registration_id: int,
    session: Session = Depends(get_db)
):
    """
    根据ID查询单个挂号记录

    - **registration_id**: 挂号记录ID
    """
    try:
        registration = session.query(Registration).filter(
            Registration.id == registration_id,
            Registration.deleted_at.is_(None)
        ).first()

        if not registration:
            log.warning(f"挂号记录不存在: ID={registration_id}")
            return error_response(msg="挂号记录不存在", code=404)

        log.info(f"查询挂号记录成功: ID={registration_id}")
        return success_response(
            data=RegistrationResponse.model_validate(registration).model_dump()
        )

    except Exception as e:
        log.error(f"查询挂号记录失败: {str(e)}")
        return error_response(msg=f"查询挂号记录失败: {str(e)}", code=500)


@router.get("/by-number/{registration_number}", response_model=ResponseModel, summary="根据挂号编号查询", dependencies=[Depends(get_current_user_info), Depends(require_permission('REGISTRATION_VIEW'))])
async def get_registration_by_number(
    registration_number: str,
    session: Session = Depends(get_db)
):
    """
    根据挂号编号查询挂号记录

    - **registration_number**: 挂号编号
    """
    try:
        registration = session.query(Registration).filter(
            Registration.registration_number == registration_number,
            Registration.deleted_at.is_(None)
        ).first()

        if not registration:
            log.warning(f"挂号记录不存在: 挂号编号={registration_number}")
            return error_response(msg="挂号记录不存在", code=404)

        log.info(f"根据挂号编号查询成功: {registration_number}")
        return success_response(
            data=RegistrationResponse.model_validate(registration).model_dump()
        )

    except Exception as e:
        log.error(f"根据挂号编号查询失败: {str(e)}")
        return error_response(msg=f"查询挂号记录失败: {str(e)}", code=500)


@router.put("/{registration_id}", response_model=ResponseModel, summary="更新挂号记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('REGISTRATION_EDIT'))])
async def update_registration(
    registration_id: int,
    registration_update: RegistrationUpdate,
    session: Session = Depends(get_db)
):
    """
    更新挂号记录信息

    - **registration_id**: 挂号记录ID
    - 只更新提供的字段，未提供的字段保持不变
    """
    try:
        # 查询挂号记录
        db_registration = session.query(Registration).filter(
            Registration.id == registration_id,
            Registration.deleted_at.is_(None)
        ).first()

        if not db_registration:
            log.warning(f"挂号记录不存在: ID={registration_id}")
            return error_response(msg="挂号记录不存在", code=404)

        # 如果要更新挂号编号，检查是否与其他记录冲突
        if registration_update.registration_number and registration_update.registration_number != db_registration.registration_number:
            existing = session.query(Registration).filter(
                Registration.registration_number == registration_update.registration_number,
                Registration.id != registration_id,
                Registration.deleted_at.is_(None)
            ).first()

            if existing:
                log.warning(
                    f"挂号编号已存在: {registration_update.registration_number}")
                return error_response(msg=f"挂号编号 {registration_update.registration_number} 已被使用", code=400)

        # 更新字段
        update_data = registration_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_registration, field, value)

        # 更新时间
        db_registration.updated_at = datetime.now()

        session.commit()
        session.refresh(db_registration)

        log.info(f"更新挂号记录成功: ID={registration_id}")
        return success_response(
            data=RegistrationResponse.model_validate(
                db_registration).model_dump(),
            msg="挂号记录更新成功"
        )

    except Exception as e:
        session.rollback()
        log.error(f"更新挂号记录失败: {str(e)}")
        return error_response(msg=f"更新挂号记录失败: {str(e)}", code=500)


@router.delete("/{registration_id}", response_model=ResponseModel, summary="删除单个挂号记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('REGISTRATION_DELETE'))])
async def delete_registration(
    registration_id: int,
    session: Session = Depends(get_db)
):
    """
    软删除单个挂号记录

    - **registration_id**: 挂号记录ID
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        registration = session.query(Registration).filter(
            Registration.id == registration_id,
            Registration.deleted_at.is_(None)
        ).first()

        if not registration:
            log.warning(f"挂号记录不存在: ID={registration_id}")
            return error_response(msg="挂号记录不存在", code=404)

        # 软删除
        registration.deleted_at = datetime.now()
        session.commit()

        log.info(f"删除挂号记录成功: ID={registration_id}")
        return success_response(msg="挂号记录删除成功")

    except Exception as e:
        session.rollback()
        log.error(f"删除挂号记录失败: {str(e)}")
        return error_response(msg=f"删除挂号记录失败: {str(e)}", code=500)


@router.delete("/", response_model=ResponseModel, summary="批量删除挂号记录", dependencies=[Depends(get_current_user_info), Depends(require_permission('REGISTRATION_DELETE'))])
async def batch_delete_registrations(
    delete_request: RegistrationDeleteRequest,
    session: Session = Depends(get_db)
):
    """
    批量软删除挂号记录

    - **ids**: 要删除的挂号记录ID列表
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        registration_ids = delete_request.ids

        # 查询要删除的挂号记录
        registrations = session.query(Registration).filter(
            Registration.id.in_(registration_ids),
            Registration.deleted_at.is_(None)
        ).all()

        if not registrations:
            log.warning("没有找到要删除的挂号记录")
            return error_response(msg="没有找到要删除的挂号记录", code=404)

        # 批量软删除
        deleted_count = 0
        deleted_ids = []

        for registration in registrations:
            registration.deleted_at = datetime.now()
            deleted_ids.append(registration.id)
            deleted_count += 1

        skipped_count = len(registration_ids) - deleted_count

        session.commit()

        log.info(f"批量删除挂号记录成功: 删除数={deleted_count}, 跳过数={skipped_count}")
        return success_response(msg=f"成功删除 {deleted_count} 条挂号记录", data={
            "deleted_count": deleted_count,
            "skipped_count": skipped_count,
            "deleted_ids": deleted_ids
        })

    except Exception as e:
        session.rollback()
        log.error(f"批量删除挂号记录失败: {str(e)}")
        return error_response(msg=f"批量删除挂号记录失败: {str(e)}", code=500)
