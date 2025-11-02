"""
检查管理API
提供检查记录的完整CRUD功能，包括：
- 创建检查记录
- 查询检查记录（单个查询、翻页查询）
- 更新检查记录
- 删除检查记录（单个删除、批量删除，软删除）
"""
from typing import Optional, List
from datetime import datetime, date, time as time_type
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_, text
from pydantic import BaseModel, Field as PydanticField

from models.examination import Examination
from models.examination_type import ExaminationType
from models.user import User
from models.fundus_image import FundusImage
from database import get_db
from utils.response import success_response, error_response, ResponseModel
from loguru_logging import log

router = APIRouter()

# ==================== 检查编号自动生成工具函数 ====================

def get_or_create_sequence_for_today(session: Session, today: str) -> str:
    """
    获取或创建今天的序列
    
    Args:
        session: 数据库会话
        today: 日期字符串，格式: YYYYMMDD
        
    Returns:
        str: 序列名称
    """
    seq_name = f"ex_seq_{today}"
    
    # 使用原生SQL创建序列（如果不存在）
    create_seq_sql = text(f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_class 
                WHERE relname = '{seq_name}' AND relkind = 'S'
            ) THEN
                EXECUTE 'CREATE SEQUENCE {seq_name} START 1';
            END IF;
        END$$;
    """)
    
    session.execute(create_seq_sql)
    session.commit()
    
    return seq_name


def generate_examination_number(session: Session) -> str:
    """
    生成检查编号
    格式: EXYYYYMMDD-NNNN
    例如: EX20250115-0001
    
    Args:
        session: 数据库会话
        
    Returns:
        str: 生成的检查编号
    """
    today = datetime.now().strftime("%Y%m%d")
    seq_name = get_or_create_sequence_for_today(session, today)
    
    # 获取下一个序列值
    result = session.execute(text(f"SELECT nextval('{seq_name}')"))
    seq_value = result.scalar()
    
    # 格式化检查编号
    examination_number = f"EX{today}-{seq_value:04d}"
    
    log.info(f"生成检查编号: {examination_number}")
    return examination_number


# ==================== Pydantic 模型定义 ====================

class ExaminationCreate(BaseModel):
    """检查创建模型"""
    examination_number: Optional[str] = PydanticField(None, min_length=1, max_length=50, description="检查编号（唯一），如不提供则自动生成")
    patient_id: int = PydanticField(..., gt=0, description="患者ID")
    examination_type_id: int = PydanticField(..., gt=0, description="检查类型ID")
    doctor_id: Optional[int] = PydanticField(None, gt=0, description="检查医生ID")
    technician_id: Optional[int] = PydanticField(None, gt=0, description="技师ID")
    examination_date: datetime = PydanticField(..., description="检查日期时间（将自动拆分为日期和时间）")
    eye_side: Optional[str] = PydanticField(None, description="检查眼别：left/right/both")
    chief_complaint: Optional[str] = PydanticField(None, description="主诉")
    present_illness: Optional[str] = PydanticField(None, description="现病史")
    examination_findings: Optional[str] = PydanticField(None, description="检查所见")
    preliminary_diagnosis: Optional[str] = PydanticField(None, description="初步诊断")
    recommendations: Optional[str] = PydanticField(None, description="建议")
    follow_up_date: Optional[date] = PydanticField(None, description="随访日期")
    status: str = PydanticField(default="pending", description="检查状态：pending/in_progress/completed/cancelled")
    notes: Optional[str] = PydanticField(None, description="备注")
    created_by: Optional[int] = PydanticField(None, gt=0, description="创建人ID")
    updated_by: Optional[int] = PydanticField(None, gt=0, description="更新人ID")

    class Config:
        json_schema_extra = {
            "example": {
                "patient_id": 1,
                "examination_type_id": 1,
                "doctor_id": 2,
                "examination_date": "2025-01-15T14:30:00",
                "eye_side": "both",
                "chief_complaint": "视力模糊",
                "status": "pending"
            }
        }
    
    class ConfigDict:
        # 注意：
        # 1. examination_number 如果不提供，系统会自动生成（格式: EXYYYYMMDD-NNNN）
        # 2. examination_date 接收完整的日期时间，会自动拆分为 examination_date 和 examination_time
        pass


class ExaminationUpdate(BaseModel):
    """检查更新模型"""
    examination_number: Optional[str] = PydanticField(None, min_length=1, max_length=50, description="检查编号")
    patient_id: Optional[int] = PydanticField(None, gt=0, description="患者ID")
    examination_type_id: Optional[int] = PydanticField(None, gt=0, description="检查类型ID")
    doctor_id: Optional[int] = PydanticField(None, gt=0, description="检查医生ID")
    technician_id: Optional[int] = PydanticField(None, gt=0, description="技师ID")
    examination_date: Optional[date] = PydanticField(None, description="检查日期")
    examination_time: Optional[time_type] = PydanticField(None, description="检查时间")
    eye_side: Optional[str] = PydanticField(None, description="检查眼别：left/right/both")
    chief_complaint: Optional[str] = PydanticField(None, description="主诉")
    present_illness: Optional[str] = PydanticField(None, description="现病史")
    examination_findings: Optional[str] = PydanticField(None, description="检查所见")
    preliminary_diagnosis: Optional[str] = PydanticField(None, description="初步诊断")
    recommendations: Optional[str] = PydanticField(None, description="建议")
    follow_up_date: Optional[date] = PydanticField(None, description="随访日期")
    status: Optional[str] = PydanticField(None, description="检查状态：pending/in_progress/completed/cancelled")
    notes: Optional[str] = PydanticField(None, description="备注")
    updated_by: Optional[int] = PydanticField(None, gt=0, description="更新人ID")

    class Config:
        json_schema_extra = {
            "example": {
                "status": "completed",
                "examination_findings": "眼底清晰，未见明显异常",
                "preliminary_diagnosis": "正常眼底"
            }
        }


class ExaminationTypeInfo(BaseModel):
    """检查类型信息模型"""
    id: int
    type_code: str
    type_name: str
    description: Optional[str] = None
    
    class Config:
        from_attributes = True


class UserInfo(BaseModel):
    """用户信息模型（用于医生/技师）"""
    id: int
    username: str
    full_name: Optional[str] = None
    
    class Config:
        from_attributes = True


class FundusImageInfo(BaseModel):
    """眼底图像信息模型"""
    id: int
    examination_id: int
    image_number: str
    eye_side: str
    capture_mode: str
    image_type: Optional[str] = None
    image_position: Optional[str] = None
    file_path: str
    file_name: str
    file_size: Optional[int] = None
    file_format: Optional[str] = None
    image_quality: Optional[str] = None
    resolution: Optional[str] = None
    acquisition_device: Optional[str] = None
    thumbnail_data: Optional[str] = None
    is_primary: bool
    upload_status: str
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ExaminationResponse(BaseModel):
    """检查响应模型"""
    id: int
    examination_number: str
    patient_id: int
    examination_type_id: int
    doctor_id: Optional[int]
    technician_id: Optional[int]
    examination_date: date
    examination_time: Optional[time_type]
    eye_side: Optional[str]
    chief_complaint: Optional[str]
    present_illness: Optional[str]
    examination_findings: Optional[str]
    preliminary_diagnosis: Optional[str]
    recommendations: Optional[str]
    follow_up_date: Optional[date]
    status: str
    notes: Optional[str]
    deleted_at: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    created_by: Optional[int]
    updated_by: Optional[int]
    # 关联信息
    examination_type: Optional[ExaminationTypeInfo] = None
    doctor: Optional[UserInfo] = None
    technician: Optional[UserInfo] = None
    fundus_images: Optional[List[FundusImageInfo]] = None

    class Config:
        from_attributes = True


class ExaminationDeleteRequest(BaseModel):
    """检查批量删除请求模型"""
    examination_ids: List[int] = PydanticField(..., min_length=1, description="要删除的检查ID列表")

# ==================== API 端点 ====================

@router.post("/", response_model=ResponseModel, summary="创建检查记录")
async def create_examination(
    examination: ExaminationCreate,
    session: Session = Depends(get_db)
):
    """
    创建新的检查记录
    
    - **examination_number**: 检查编号，如不提供则自动生成（格式：EXYYYYMMDD-NNNN）
    - **patient_id**: 患者ID
    - **examination_type_id**: 检查类型ID
    - **examination_date**: 检查日期时间（格式：YYYY-MM-DDTHH:MM:SS 或 YYYY-MM-DD HH:MM:SS）
    - **status**: 检查状态（pending/in_progress/completed/cancelled）
    
    注意：examination_date 会自动拆分为 examination_date（日期）和 examination_time（时间）存储
    """
    try:
        # 如果没有提供检查编号，则自动生成
        if not examination.examination_number:
            examination.examination_number = generate_examination_number(session)
            log.info(f"自动生成检查编号: {examination.examination_number}")
        
        # 检查检查编号是否已存在
        existing = session.query(Examination).filter(
            Examination.examination_number == examination.examination_number,
            Examination.deleted_at.is_(None)
        ).first()
        
        if existing:
            log.warning(f"检查编号已存在: {examination.examination_number}")
            return error_response(msg=f"检查编号 {examination.examination_number} 已存在", code=400)
        
        # 将 Pydantic 模型转为字典
        examination_dict = examination.model_dump()
        
        # 拆分日期时间
        examination_datetime = examination_dict.pop('examination_date')
        if isinstance(examination_datetime, datetime):
            # 拆分为日期和时间
            examination_dict['examination_date'] = examination_datetime.date()
            examination_dict['examination_time'] = examination_datetime.time()
            log.info(f"拆分日期时间: 日期={examination_dict['examination_date']}, 时间={examination_dict['examination_time']}")
        else:
            # 如果是其他类型，直接使用
            examination_dict['examination_date'] = examination_datetime
            examination_dict['examination_time'] = None
        
        # 创建新检查记录
        db_examination = Examination(**examination_dict)
        session.add(db_examination)
        session.commit()
        session.refresh(db_examination)
        
        log.info(f"成功创建检查记录: ID={db_examination.id}, 检查编号={db_examination.examination_number}")
        return success_response(
            data=ExaminationResponse.model_validate(db_examination).model_dump(),
            msg="检查记录创建成功"
        )
    
    except Exception as e:
        session.rollback()
        log.error(f"创建检查记录失败: {str(e)}")
        return error_response(msg=f"创建检查记录失败: {str(e)}", code=500)


@router.get("/", response_model=ResponseModel, summary="分页查询检查记录")
async def get_examinations(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=100, description="每页数量"),
    patient_id: Optional[int] = Query(None, description="按患者ID筛选"),
    doctor_id: Optional[int] = Query(None, description="按医生ID筛选"),
    examination_type_id: Optional[int] = Query(None, description="按检查类型ID筛选"),
    status: Optional[str] = Query(None, description="按状态筛选"),
    examination_number: Optional[str] = Query(None, description="按检查编号筛选"),
    start_date: Optional[date] = Query(None, description="开始日期"),
    end_date: Optional[date] = Query(None, description="结束日期"),
    include_deleted: bool = Query(False, description="是否包含已删除记录"),
    session: Session = Depends(get_db)
):
    """
    分页查询检查记录列表
    
    支持多种筛选条件：
    - 患者ID
    - 医生ID
    - 检查类型ID
    - 检查状态
    - 检查编号
    - 日期范围
    """
    try:
        # 构建基础查询 - 用于计算总数
        count_query = session.query(Examination)
        
        # 应用筛选条件
        if not include_deleted:
            count_query = count_query.filter(Examination.deleted_at.is_(None))
        
        if patient_id:
            count_query = count_query.filter(Examination.patient_id == patient_id)
        
        if doctor_id:
            count_query = count_query.filter(Examination.doctor_id == doctor_id)
        
        if examination_type_id:
            count_query = count_query.filter(Examination.examination_type_id == examination_type_id)
        
        if status:
            count_query = count_query.filter(Examination.status == status)
        
        if examination_number:
            count_query = count_query.filter(Examination.examination_number.ilike(f"%{examination_number}%"))
        
        if start_date:
            count_query = count_query.filter(Examination.examination_date >= start_date)
        
        if end_date:
            count_query = count_query.filter(Examination.examination_date <= end_date)
        
        # 计算总数
        total = count_query.count()
        
        # 重新构建查询用于分页数据获取
        data_query = session.query(Examination)
        
        # 应用相同的筛选条件
        if not include_deleted:
            data_query = data_query.filter(Examination.deleted_at.is_(None))
        
        if patient_id:
            data_query = data_query.filter(Examination.patient_id == patient_id)
        
        if doctor_id:
            data_query = data_query.filter(Examination.doctor_id == doctor_id)
        
        if examination_type_id:
            data_query = data_query.filter(Examination.examination_type_id == examination_type_id)
        
        if status:
            data_query = data_query.filter(Examination.status == status)
        
        if examination_number:
            data_query = data_query.filter(Examination.examination_number.ilike(f"%{examination_number}%"))
        
        if start_date:
            data_query = data_query.filter(Examination.examination_date >= start_date)
        
        if end_date:
            data_query = data_query.filter(Examination.examination_date <= end_date)
        
        # 分页
        offset = (page - 1) * page_size
        examinations = data_query.order_by(Examination.examination_date.desc(), Examination.id.desc())\
                           .offset(offset)\
                           .limit(page_size)\
                           .all()
        
        # 转换为响应模型，并添加关联信息
        examination_list = []
        for exam in examinations:
            exam_dict = ExaminationResponse.model_validate(exam).model_dump()
            
            # 查询关联的检查类型
            if exam.examination_type_id:
                exam_type = session.query(ExaminationType).filter(
                    ExaminationType.id == exam.examination_type_id
                ).first()
                if exam_type:
                    exam_dict['examination_type'] = ExaminationTypeInfo.model_validate(exam_type).model_dump()
            
            # 查询关联的医生
            if exam.doctor_id:
                doctor = session.query(User).filter(User.id == exam.doctor_id).first()
                if doctor:
                    exam_dict['doctor'] = UserInfo.model_validate(doctor).model_dump()
            
            # 查询关联的技师
            if exam.technician_id:
                technician = session.query(User).filter(User.id == exam.technician_id).first()
                if technician:
                    exam_dict['technician'] = UserInfo.model_validate(technician).model_dump()
            
            examination_list.append(exam_dict)
        
        log.info(f"查询检查记录列表成功: 页码={page}, 每页={page_size}, 总数={total}")
        return success_response(data={
            "items": examination_list,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size
        })
    
    except Exception as e:
        log.error(f"查询检查记录列表失败: {str(e)}")
        return error_response(msg=f"查询检查记录列表失败: {str(e)}", code=500)


@router.get("/{examination_id}", response_model=ResponseModel, summary="查询单个检查记录")
async def get_examination(
    examination_id: int,
    session: Session = Depends(get_db)
):
    """
    根据ID查询单个检查记录
    
    - **examination_id**: 检查记录ID
    """
    try:
        examination = session.query(Examination).filter(
            Examination.id == examination_id,
            Examination.deleted_at.is_(None)
        ).first()
        
        if not examination:
            log.warning(f"检查记录不存在: ID={examination_id}")
            return error_response(msg="检查记录不存在", code=404)
        
        # 构建响应数据，包含关联信息
        exam_dict = ExaminationResponse.model_validate(examination).model_dump()
        
        # 查询关联的检查类型
        if examination.examination_type_id:
            exam_type = session.query(ExaminationType).filter(
                ExaminationType.id == examination.examination_type_id
            ).first()
            if exam_type:
                exam_dict['examination_type'] = ExaminationTypeInfo.model_validate(exam_type).model_dump()
        
        # 查询关联的医生
        if examination.doctor_id:
            doctor = session.query(User).filter(User.id == examination.doctor_id).first()
            if doctor:
                exam_dict['doctor'] = UserInfo.model_validate(doctor).model_dump()
        
        # 查询关联的技师
        if examination.technician_id:
            technician = session.query(User).filter(User.id == examination.technician_id).first()
            if technician:
                exam_dict['technician'] = UserInfo.model_validate(technician).model_dump()
        
        # 查询关联的眼底图像
        fundus_images = session.query(FundusImage).filter(
            FundusImage.examination_id == examination_id,
            FundusImage.deleted_at.is_(None)
        ).order_by(FundusImage.is_primary.desc(), FundusImage.created_at.asc()).all()
        
        if fundus_images:
            exam_dict['fundus_images'] = [
                FundusImageInfo.model_validate(img).model_dump() 
                for img in fundus_images
            ]
            log.info(f"查询到 {len(fundus_images)} 张眼底图像")
        else:
            exam_dict['fundus_images'] = []
        
        log.info(f"查询检查记录成功: ID={examination_id}")
        return success_response(data=exam_dict)
    
    except Exception as e:
        log.error(f"查询检查记录失败: {str(e)}")
        return error_response(msg=f"查询检查记录失败: {str(e)}", code=500)


@router.get("/by-number/{examination_number}", response_model=ResponseModel, summary="根据检查编号查询")
async def get_examination_by_number(
    examination_number: str,
    session: Session = Depends(get_db)
):
    """
    根据检查编号查询检查记录
    
    - **examination_number**: 检查编号
    """
    try:
        examination = session.query(Examination).filter(
            Examination.examination_number == examination_number,
            Examination.deleted_at.is_(None)
        ).first()
        
        if not examination:
            log.warning(f"检查记录不存在: 检查编号={examination_number}")
            return error_response(msg="检查记录不存在", code=404)
        
        log.info(f"根据检查编号查询成功: {examination_number}")
        return success_response(
            data=ExaminationResponse.model_validate(examination).model_dump()
        )
    
    except Exception as e:
        log.error(f"根据检查编号查询失败: {str(e)}")
        return error_response(msg=f"查询检查记录失败: {str(e)}", code=500)


@router.put("/{examination_id}", response_model=ResponseModel, summary="更新检查记录")
async def update_examination(
    examination_id: int,
    examination_update: ExaminationUpdate,
    session: Session = Depends(get_db)
):
    """
    更新检查记录信息
    
    - **examination_id**: 检查记录ID
    - 只更新提供的字段，未提供的字段保持不变
    """
    try:
        # 查询检查记录
        db_examination = session.query(Examination).filter(
            Examination.id == examination_id,
            Examination.deleted_at.is_(None)
        ).first()
        
        if not db_examination:
            log.warning(f"检查记录不存在: ID={examination_id}")
            return error_response(msg="检查记录不存在", code=404)
        
        # 如果要更新检查编号，检查是否与其他记录冲突
        if examination_update.examination_number and examination_update.examination_number != db_examination.examination_number:
            existing = session.query(Examination).filter(
                Examination.examination_number == examination_update.examination_number,
                Examination.id != examination_id,
                Examination.deleted_at.is_(None)
            ).first()
            
            if existing:
                log.warning(f"检查编号已存在: {examination_update.examination_number}")
                return error_response(msg=f"检查编号 {examination_update.examination_number} 已被使用", code=400)
        
        # 更新字段
        update_data = examination_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_examination, field, value)
        
        # 更新时间
        db_examination.updated_at = datetime.now()
        
        session.commit()
        session.refresh(db_examination)
        
        log.info(f"更新检查记录成功: ID={examination_id}")
        return success_response(
            data=ExaminationResponse.model_validate(db_examination).model_dump(),
            msg="检查记录更新成功"
        )
    
    except Exception as e:
        session.rollback()
        log.error(f"更新检查记录失败: {str(e)}")
        return error_response(msg=f"更新检查记录失败: {str(e)}", code=500)


@router.delete("/{examination_id}", response_model=ResponseModel, summary="删除单个检查记录")
async def delete_examination(
    examination_id: int,
    session: Session = Depends(get_db)
):
    """
    软删除单个检查记录
    
    - **examination_id**: 检查记录ID
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        examination = session.query(Examination).filter(
            Examination.id == examination_id,
            Examination.deleted_at.is_(None)
        ).first()
        
        if not examination:
            log.warning(f"检查记录不存在: ID={examination_id}")
            return error_response(msg="检查记录不存在", code=404)
        
        # 软删除
        examination.deleted_at = datetime.now()
        session.commit()
        
        log.info(f"删除检查记录成功: ID={examination_id}")
        return success_response(msg="检查记录删除成功")
    
    except Exception as e:
        session.rollback()
        log.error(f"删除检查记录失败: {str(e)}")
        return error_response(msg=f"删除检查记录失败: {str(e)}", code=500)


@router.delete("/", response_model=ResponseModel, summary="批量删除检查记录")
async def batch_delete_examinations(
    delete_request: ExaminationDeleteRequest,
    session: Session = Depends(get_db)
):
    """
    批量软删除检查记录
    
    - **examination_ids**: 要删除的检查记录ID列表
    - 使用软删除，记录不会真正从数据库中删除
    """
    try:
        examination_ids = delete_request.examination_ids
        
        # 查询要删除的检查记录
        examinations = session.query(Examination).filter(
            Examination.id.in_(examination_ids),
            Examination.deleted_at.is_(None)
        ).all()
        
        if not examinations:
            log.warning("没有找到要删除的检查记录")
            return error_response(msg="没有找到要删除的检查记录", code=404)
        
        # 批量软删除
        deleted_count = 0
        skipped_count = 0
        deleted_ids = []
        
        for examination in examinations:
            examination.deleted_at = datetime.now()
            deleted_ids.append(examination.id)
            deleted_count += 1
        
        skipped_count = len(examination_ids) - deleted_count
        
        session.commit()
        
        log.info(f"批量删除检查记录成功: 删除数={deleted_count}, 跳过数={skipped_count}")
        return success_response(msg=f"成功删除 {deleted_count} 条检查记录", data={
            "deleted_count": deleted_count,
            "skipped_count": skipped_count,
            "deleted_ids": deleted_ids
        })
    
    except Exception as e:
        session.rollback()
        log.error(f"批量删除检查记录失败: {str(e)}")
        return error_response(msg=f"批量删除检查记录失败: {str(e)}", code=500)