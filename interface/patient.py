"""
患者管理API
"""
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from database import db, DatabaseError
from models.patient import Patient

router = APIRouter()


class PatientBase(BaseModel):
    """患者基础模型"""
    name: str
    gender: str
    birth_date: str
    id_card: str
    phone: str
    address: str = None
    medical_history: str = None
    allergies: str = None
    emergency_contact: str = None
    emergency_phone: str = None


class PatientCreate(PatientBase):
    """患者创建模型"""
    pass


class PatientResponse(PatientBase):
    """患者响应模型"""
    id: int

    class Config:
        from_attributes = True


@router.post("/", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
async def create_patient(patient_data: PatientCreate):
    """创建新患者"""
    try:
        new_patient = Patient(**patient_data.dict())
        created_patient = db.create(new_patient)
        return created_patient
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )


@router.get("/", response_model=List[PatientResponse])
async def get_patients():
    """获取所有患者"""
    try:
        patients = db.get_all(Patient)
        return patients
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )


@router.get("/{patient_id}", response_model=PatientResponse)
async def get_patient(patient_id: int):
    """根据ID获取患者"""
    try:
        patient = db.get_by_id(Patient, patient_id)
        if not patient:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"患者ID {patient_id} 不存在"
            )
        return patient
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )