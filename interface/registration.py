"""
挂号管理API
"""
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from database import db, DatabaseError
from models.registration import Registration

router = APIRouter()


class RegistrationResponse(BaseModel):
    """挂号响应模型"""
    id: int
    patient_id: int
    examination_type_id: int
    doctor_id: int
    status: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[RegistrationResponse])
async def get_registrations():
    """获取所有挂号记录"""
    try:
        registrations = db.get_all(Registration)
        return registrations
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )