"""
检查管理API
"""
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from database import db, DatabaseError
from models.examination import Examination

router = APIRouter()


class ExaminationResponse(BaseModel):
    """检查响应模型"""
    id: int
    patient_id: int
    doctor_id: int
    examination_type_id: int
    diagnosis: str = None
    status: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[ExaminationResponse])
async def get_examinations():
    """获取所有检查"""
    try:
        examinations = db.get_all(Examination)
        return examinations
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )