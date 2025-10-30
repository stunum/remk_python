"""
眼底图像管理API
"""
from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from database import db, DatabaseError
from models.fundus_image import FundusImage

router = APIRouter()


class FundusImageResponse(BaseModel):
    """眼底图像响应模型"""
    id: int
    examination_id: int
    eye_side: str
    file_path: str
    file_name: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[FundusImageResponse])
async def get_fundus_images():
    """获取所有眼底图像"""
    try:
        images = db.get_all(FundusImage)
        return images
    except DatabaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"数据库错误: {str(e)}"
        )